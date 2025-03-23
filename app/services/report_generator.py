from app.services.interfaces.i_report_generator import IReportGenerator


class ReportGenerator(IReportGenerator):
    def start_generation(
        self, report_type, template, progress_callback, status_callback, result_callback
    ):
        # Implement the generation logic
        pass

    def pause_generation(self):
        # Implement the pause logic
        pass

    def stop_generation(self):
        # Implement the stop logic
        pass

    def get_status(self):
        # Implement the status retrieval logic
        return "Status message"

    def save_report(self, file_name):
        # Implement the save logic
        pass
