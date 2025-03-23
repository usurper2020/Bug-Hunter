from abc import ABC, abstractmethod


class IReportGenerator(ABC):
    @abstractmethod
    def start_generation(
        self, report_type, template, progress_callback, status_callback, result_callback
    ):
        pass

    @abstractmethod
    def pause_generation(self):
        pass

    @abstractmethod
    def stop_generation(self):
        pass

    @abstractmethod
    def get_status(self):
        pass

    @abstractmethod
    def save_report(self, file_name):
        pass
