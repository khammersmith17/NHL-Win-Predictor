import joblib
import xgboost

class ModelScorer:
    def __init__(self):
        self.model=joblib.load('win-model/model.joblib')

    def run_inference(self, X):
        y = self.model.predict(X)