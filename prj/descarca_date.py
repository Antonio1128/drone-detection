from roboflow import Roboflow

# Conectarea la platformă
rf = Roboflow(api_key="XcLN07YiCDrqtmMZ39Gl")

# Selectarea proiectului de detecție drone public
project = rf.workspace("drone-detection-project").project("drone-detection-yolov8")

# Descărcarea automată a dataset-ului direct în folderul tău din VS Code
dataset = project.version(1).download("yolov8")
print("Dataset descărcat cu succes!")