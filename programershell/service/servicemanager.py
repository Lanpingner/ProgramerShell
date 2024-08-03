from service.datacollector import DataCollector
from service.hyprland import Hyprland


def startServices():
    metrics_thread = DataCollector()
    metrics_thread.daemon = True
    metrics_thread.start()
    hypr = Hyprland()
    hypr.start()
