import pytest
from app.model_validation import ReviewedPrediction, evaluate

def row(sample,site,split,score,label,weather="clear",light="day"):
    return ReviewedPrediction(sample_id=sample,site_id=site,split=split,
        modality="acoustic",target="chainsaw",weather=weather,light=light,
        score=score,verified_label=label,reviewer_id="ranger-1",model_version="candidate-v1")

def test_site_holdout_metrics():
    r=[row("a","site-a","train",.8,True),
       row("b","site-b","test",.9,True),
       row("c","site-b","test",.9,False),
       row("d","site-b","test",.2,False),
       row("e","site-b","test",.2,True,light="night")]
    output=evaluate(r)
    assert output["overall"]["precision"]==0.5
    assert output["overall"]["recall"]==0.5
    assert output["overall"]["tn"]==1
    assert "light:night" in output["strata"]

def test_site_leakage_rejected():
    with pytest.raises(ValueError,match="Site leakage"):
        evaluate([row("a","same","train",.7,True),row("b","same","test",.7,True)])

def test_no_test_rejected():
    with pytest.raises(ValueError,match="No independent test"):
        evaluate([row("a","site-a","train",.7,True)])

def test_duplicate_ids_rejected():
    with pytest.raises(ValueError,match="Duplicate"):
        evaluate([row("a","site-a","test",.7,True),row("a","site-b","test",.2,False)])
