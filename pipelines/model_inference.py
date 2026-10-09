"""Actual ONNX inference for audio windows or camera crops. Model assets not bundled."""
import json
import numpy as np
class ValidatedModel:
    def __init__(self,weights,manifest):
        self.manifest=json.load(open(manifest,encoding="utf8"))
        if self.manifest.get("deployment_approved") is not True:
            raise ValueError("Model has not passed deployment validation")
        if not self.manifest.get("validation_dataset") or not self.manifest.get("class_names"):
            raise ValueError("Missing validation evidence")
        import onnxruntime as ort
        self.session=ort.InferenceSession(weights,providers=["CPUExecutionProvider"])
        self.input=self.session.get_inputs()[0]
    def predict(self,data):
        x=np.asarray(data,dtype=np.float32)
        output=self.session.run(None,{self.input.name:x})[0]
        return {"scores":np.asarray(output).tolist(),"classes":self.manifest["class_names"],
                "model_id":self.manifest.get("model_id"),"calibrated":self.manifest.get("calibrated",False)}
