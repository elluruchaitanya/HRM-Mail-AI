positive_words = {"awesome","back","best","big","blessed","breeze","bravo","breathtaking","cares","celebrities","celebrate","celebrations","chose","clean","cleanliness","cocktail","come back","comfort","comfortable","coordinated","courteous","customer service","definitely","delight","delicious","detail","each time","efficient","elegant","empathic","ensured","enthusiastic","epic","exceeded","excellent","expected","experience","extremely","fabulous","festive","first-class","fitness center","free","friendliness","friendly","gem","genuinely","go again","gorgeous","grande","greeted","great","great place","groomed","happy","hard work","happen","healpful","helpful","history","historic","historical","impeccable","impressed","improved","incredible","institution","joy","kind","knowledge","knowledgeable","large","lively","look forward","love","love to come back","loved","lovely","made","minimal","movie theater","nicely","nicely furnished","one of a kind","outstanding","outdid","perfect","phenomenal","precious","pride","professional","professionalism","quickly","quiet","recommend","recommends","relaxing","remarkable","remember","resolved","response","returning","royally","safe","security","set up","sleek","smile","spacious","special","stately","stylish","stunning","superb","surprising","sweet","tasty","thoughtful","top","top-notch","treat","try","terrific","upgraded","upgrade","valued","voucher","warmth","well maintained","well-appointed","welcoming","will return","wonderful","worth it"}
neutral_words = {"accountable","amazing","appalling","atmosphere","awesome","back up traffic","beautiful place","blood","carpeted","charm","coolest thing","comfortable","couldn’t","crisp","dated","details","disappointing","dog policy","don’t","don’t expect","early","expensive","fabulous","fault","friendly","full","good","great","hard","historical","homeless","huge","interesting","kicked","lacking","lied","like","lovely","lost power","low","magnificient","manipulate","missing","movie","neat","never restored","nice","noisy","not modern","not the same","noteworthy","nothing","old","on purpose","otherwise","passing the buck","replacing","resolved","room","salty","small","smoke","spacious","stain","stains","stale","strip","super","true pet policy","turns","twists","uncomfortable","uninteresting","updating","vintage","waiting","well-equipped","wished","worse","worn"}
negative_words = {"affected","assaulted","bad","bitter","bug","charge","cleaned","complaint","communicated","construction","dated","disruption","dirt","didn’t","elevator shaft","eat","expect","extremely","fee","free","issue","kick","leak","like","little cleaner","low","mildew","moved around","never","never again","no one answered","nor","not","not cleaned","not Royal Senesta standards","out of date","overmatched","paid way too much","pinched","problem","racism","refresh","reprimand","reconsider","scuffed","see movie","shabby","slipping","smelled","tired","trashcan","undertrained","unacceptable","unfortunate","unfortunately","upset","very old","waste","woke us up","wish","wouldn't help","work going on"}

def get_sentiment_score(tokens):
    score = 0
    for token in tokens:
        if token in positive_words:
            score += 1
        elif token in negative_words:
            score -= 1
    return score
from transformers import DistilBertTokenizerFast

tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

def preprocess_text(text):
    tokens = tokenizer.tokenize(text)
    sentiment_score = get_sentiment_score(tokens)
    return tokenizer(text, truncation=True, padding="max_length"), sentiment_score

from datasets import load_dataset

file_path = "Datasets\cleaned_data.json"
dataset = load_dataset("json", data_files=file_path, split='train')

def format_data(example):
    tokens, score = preprocess_text(example["text"])
    example["input_ids"] = tokens["input_ids"]
    example["attention_mask"] = tokens["attention_mask"]
    example["sentiment_score"] = score
    return example

tokenized_dataset = dataset.map(format_data)
test_data = dataset.map(format_data)

from transformers import DistilBertTokenizerFast

tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

def preprocess_text(text):
    tokens = tokenizer.tokenize(text)
    sentiment_score = get_sentiment_score(tokens)
    return tokenizer(text, truncation=True, padding="max_length"), sentiment_score

import torch
from transformers import DistilBertForSequenceClassification

model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=3)

# Adjust model to include lexicon-based scores
class SentimentDistilBERT(torch.nn.Module):
    def __init__(self, model):
        super(SentimentDistilBERT, self).__init__()
        self.distilbert = model.distilbert
        self.classifier = model.classifier
        self.fc_sentiment = torch.nn.Linear(1, 3)  # Incorporates lexicon scores
        self.loss_fn = torch.nn.CrossEntropyLoss()  

    def forward(self, input_ids, attention_mask, sentiment_score, labels=None):
        outputs = self.distilbert(input_ids=input_ids, attention_mask=attention_mask)
        logits = self.classifier(outputs.last_hidden_state[:, 0, :])
        sentiment_adjusted = self.fc_sentiment(sentiment_score.unsqueeze(1).float())
        logits += sentiment_adjusted  # Adjust sentiment score

        if labels is not None:
            loss = self.loss_fn(logits, labels)
            return {"loss": loss, "logits": logits}
        return {"logits": logits}

model = SentimentDistilBERT(model)

from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
   output_dir="./results",
    eval_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=5,
    num_train_epochs=3,
    weight_decay=0.01,
)

trainer = Trainer(
     model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    eval_dataset=tokenized_dataset
)

trainer.train()

# Evaluate the model
eval_results = trainer.evaluate()
print(eval_results)

torch.save(model.state_dict(), "fine_tuned_distilbert.pth")  # Save the trained model's weights
torch.save(model, "fine_tuned_distilbert_full.pth")
#model.save_pretrained("./fine_tuned_distilbert")
tokenizer.save_pretrained("./fine_tuned_distilbert")


