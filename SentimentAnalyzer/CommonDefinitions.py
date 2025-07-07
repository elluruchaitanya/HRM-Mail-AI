import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
class MethodsToTrainAndLoad:
    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=3)
    positive_words = {"awesome","back","best","big","blessed","breeze","bravo","breathtaking","cares","celebrities","celebrate","celebrations","chose","clean","cleanliness","cocktail","come back","comfort","comfortable","coordinated","courteous","customer service","definitely","delight","delicious","detail","each time","efficient","elegant","empathic","ensured","enthusiastic","epic","exceeded","excellent","expected","experience","extremely","fabulous","festive","first-class","fitness center","free","friendliness","friendly","gem","genuinely","go again","gorgeous","grande","greeted","great","great place","groomed","happy","hard work","happen","healpful","helpful","history","historic","historical","impeccable","impressed","improved","incredible","institution","joy","kind","knowledge","knowledgeable","large","lively","look forward","love","love to come back","loved","lovely","made","minimal","movie theater","nicely","nicely furnished","one of a kind","outstanding","outdid","perfect","phenomenal","precious","pride","professional","professionalism","quickly","quiet","recommend","recommends","relaxing","remarkable","remember","resolved","response","returning","royally","safe","security","set up","sleek","smile","spacious","special","stately","stylish","stunning","superb","surprising","sweet","tasty","thoughtful","top","top-notch","treat","try","terrific","upgraded","upgrade","valued","voucher","warmth","well maintained","well-appointed","welcoming","will return","wonderful","worth it"}
    neutral_words = {"accountable","amazing","appalling","atmosphere","awesome","back up traffic","beautiful place","blood","carpeted","charm","coolest thing","comfortable","couldn’t","crisp","dated","details","disappointing","dog policy","don’t","don’t expect","early","expensive","fabulous","fault","friendly","full","good","great","hard","historical","homeless","huge","interesting","kicked","lacking","lied","like","lovely","lost power","low","magnificient","manipulate","missing","movie","neat","never restored","nice","noisy","not modern","not the same","noteworthy","nothing","old","on purpose","otherwise","passing the buck","replacing","resolved","room","salty","small","smoke","spacious","stain","stains","stale","strip","super","true pet policy","turns","twists","uncomfortable","uninteresting","updating","vintage","waiting","well-equipped","wished","worse","worn"}
    negative_words = {"affected","assaulted","bad","bitter","bug","charge","cleaned","complaint","communicated","construction","dated","disruption","dirt","didn’t","elevator shaft","eat","expect","extremely","fee","free","issue","kick","leak","like","little cleaner","low","mildew","moved around","never","never again","no one answered","nor","not","not cleaned","not Royal Senesta standards","out of date","overmatched","paid way too much","pinched","problem","racism","refresh","reprimand","reconsider","scuffed","see movie","shabby","slipping","smelled","tired","trashcan","undertrained","unacceptable","unfortunate","unfortunately","upset","very old","waste","woke us up","wish","wouldn't help","work going on"}

    def get_sentiment_score(tokens):
        score = 0
        for token in tokens:
            if token in MethodsToTrainAndLoad.positive_words:
                score += 1
            elif token in MethodsToTrainAndLoad.negative_words:
                score -= 1
        return score
    def preprocess_text(text):
        tokens = MethodsToTrainAndLoad.tokenizer.tokenize(text)
        sentiment_score = MethodsToTrainAndLoad.get_sentiment_score(tokens)  # Use lexicon-based scoring
        return MethodsToTrainAndLoad.tokenizer(text, truncation=True, padding="max_length", return_tensors="pt"), torch.tensor([sentiment_score], dtype=torch.float)

    def predict_sentiment(text):
        inputs, sentiment_score = MethodsToTrainAndLoad.preprocess_text(text)

        with torch.no_grad():  # No gradient calculation needed for inference
            outputs = MethodsToTrainAndLoad.model(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"], sentiment_score=sentiment_score)

        logits = outputs["logits"]
        predicted_class = torch.argmax(logits, dim=1).item()

        sentiment_labels = ["Negative", "Neutral", "Positive"]
        return sentiment_labels[predicted_class]
