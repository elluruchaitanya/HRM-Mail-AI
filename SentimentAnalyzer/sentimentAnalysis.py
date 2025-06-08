import torch
from SentimentAnalyzer.SentimentDistilBERTDef import SentimentDistilBERT
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from SentimentAnalyzer.CommonDefinitions import MethodsToTrainAndLoad

model = SentimentDistilBERT(MethodsToTrainAndLoad.model)
# Load trained weights
model.load_state_dict(torch.load("DistilBERT/fine_tuned_distilbert.pth"))
model.eval()  # Switch to evaluation mode

def predict_sentiment(text):
    inputs, sentiment_score = MethodsToTrainAndLoad.preprocess_text(text)

    with torch.no_grad():  # No gradient calculation needed for inference
        outputs = model(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"], sentiment_score=sentiment_score)

    logits = outputs["logits"]
    predicted_class = torch.argmax(logits, dim=1).item()

    sentiment_labels = ["Negative", "Neutral", "Positive"]
    return sentiment_labels[predicted_class]

def AnalyzeSentiment(inputText):
# Example usage
#text = "I reported this hotel to the fire marshal for a fire hazard they’re investigating the hotel now. Elevators were broken. No one told us and the management is not cooperating they could care less about their customers even though hotel supposed to have four stars!! Service was terrible. The hostess didn’t. Let me know where he seated my friend. Would stay somewhere else"
    return predict_sentiment(inputText)