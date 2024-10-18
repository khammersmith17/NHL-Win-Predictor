import xgboost as xgb

class ModelScorer:
    def __init__(self):
        self.model=xgb.XGBClassifier(objective='binary:logistic')
        self.get_model()

    def get_model(self):
        self.model.load_model("model")

    def run_inference(self, X):
        y = self.model.predict(X)

        return y

