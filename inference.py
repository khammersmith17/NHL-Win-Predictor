import xgboost as xgb

class ModelScorer:
    def __init__(self):
        self.model=xgb.XGBClassifier(objective='binary:logistic')

    async def get_model(self):
        self.model.load_model("model")

    async def run_inference(self, X):
        y = self.model.predict(X)

        return y

model = ModelScorer()
