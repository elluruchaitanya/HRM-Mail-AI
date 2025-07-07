import torch
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
