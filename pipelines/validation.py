"""Evaluate a binary gunshot candidate classifier on independent labeled samples."""
import argparse,json
import numpy as np
from sklearn.metrics import precision_recall_fscore_support,confusion_matrix,roc_auc_score
def evaluate(y_true,scores,threshold=.5):
    y=np.asarray(y_true,dtype=int);p=np.asarray(scores,dtype=float)
    if len(y)!=len(p) or not len(y):raise ValueError("Samples missing/mismatched")
    pred=(p>=threshold).astype(int)
    precision,recall,f1,_=precision_recall_fscore_support(y,pred,average="binary",zero_division=0)
    cm=confusion_matrix(y,pred,labels=[0,1])
    return {"n":len(y),"threshold":threshold,"precision":float(precision),"recall":float(recall),
            "f1":float(f1),"false_positives":int(cm[0,1]),"false_negatives":int(cm[1,0]),
            "roc_auc":float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,
            "note":"This alone is not a field certification; evaluate across devices, seasons, geographic domains and negative sounds."}
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("labeled_json",help="JSON array of {label,score} rows");args=parser.parse_args()
    rows=json.load(open(args.labeled_json));print(json.dumps(evaluate([x["label"] for x in rows],[x["score"] for x in rows]),indent=2))
