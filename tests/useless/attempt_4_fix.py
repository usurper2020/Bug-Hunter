import os

# Define the fixes for each file
fixes = {
"Nuclei/_gauge.py": [
(8, "class GaugeValidator(_plotly_utils.basevalidators.CompoundValidator):"),
(9, "    def __init__(self, plotly_name: str = '', parent_name: str = '', **kwargs) -> None:"),
(10, "        super(GaugeValidator, self).__init__("),
(11, "            plotly_name=plotly_name,"),
(12, "            parent_name=parent_name,"),
(13, "            data_class_str=kwargs.pop('data_class_str', 'Gauge'),"),
(14, "            data_docs=kwargs.pop("),
(15, '                "data_docs",'),
(16, '                """'),
(17, "        axis"),
(18, "        :class:`plotly.graph_objects.indicator.gauge.Axis` instance or dict with compatible properties"),
(19, "        bar"),
(20, "        Set the appearance of the gauge's value"),
(21, "        bgcolor"),
(22, "        Sets the gauge background color."),
(23, "        bordercolor"),
(24, "        Sets the color of the border enclosing the gauge."),
(25, "        borderwidth"),
(26, "        Sets the width (in px) of the border enclosing the gauge."),
(27, "        shape"),
(28, "        Set the shape of the gauge"),
(29, "        steps"),
(30, "        A tuple of :class:`plotly.graph_objects.indicator.gauge.Step` instances or dicts with compatible properties"),
(31, "        stepdefaults"),
(32, "        When used in a template (as layout.template.data.indicator.gauge.stepdefaults), sets the default property values to use for elements of indicator.gauge.steps"),
(33, "        threshold"),
(34, "        :class:`plotly.graph_objects.indicator.gauge.Threshold` instance or dict with compatible properties"),
(35, '        """,'),
(36, "            ),"),
(37, "            **kwargs,"),
(38, "        )"),
],
"Nuclei/_heatmap.py": [
(5, "class HeatmapValidator(_plotly_utils.basevalidators.CompoundArrayValidator):"),
(6, "    def __init__(self, plotly_name='heatmap', parent_name='layout.template.data', **kwargs):"),
(7, "        super(HeatmapValidator, self).__init__("),
(8, "            plotly_name=plotly_name,"),
(9, "            parent_name=parent_name,"),
(10, "            data_class_str=kwargs.pop('data_class_str', 'Heatmap'),"),
(11, "            data_docs=kwargs.pop("),
(12, '                "data_docs",'),
(13, '                """'),
(14, '        """,'),
(15, "            ),"),
(16, "            **kwargs,"),
(17, "        )"),
],
"Nuclei/_heatmapgl.py": [
(5, "class HeatmapglValidator(_plotly_utils.basevalidators.CompoundArrayValidator):"),
(6, "    def __init__(self, plotly_name='heatmapgl', parent_name='layout.template.data', **kwargs):"),
(7, "        super(HeatmapglValidator, self).__init__("),
(8, "            plotly_name=plotly_name,"),
(9, "            parent_name=parent_name,"),
(10, "            data_class_str=kwargs.pop('data_class_str', 'Heatmapgl'),"),
(11, "            data_docs=kwargs.pop("),
(12, '                "data_docs",'),
(13, '                """'),
(14, '        """,'),
(15, "            ),"),
(16, "            **kwargs,"),
(17, "        )"),
],
"Nuclei/_histogram.py": [
(5, "class HistogramValidator(_plotly_utils.basevalidators.CompoundArrayValidator):"),
(6, "    def __init__(self, plotly_name='histogram', parent_name='layout.template.data', **kwargs):"),
(7, "        super(HistogramValidator, self).__init__("),
(8, "            plotly_name=plotly_name,"),
(9, "            parent_name=parent_name,"),
(10, "            data_class_str=kwargs.pop('data_class_str', 'Histogram'),"),
(11, "            data_docs=kwargs.pop("),
(12, '                "data_docs",'),
(13, '                """'),
(14, '        """,'),
(15, "            ),"),
(16, "            **kwargs,"),
(17, "        )"),
],
"Nuclei/_histogram2d.py": [
(5, "class Histogram2DValidator(_plotly_utils.basevalidators.CompoundArrayValidator):"),
(6, "    def __init__(self, plotly_name='histogram2d', parent_name='layout.template.data', **kwargs):"),
(7, "        super(Histogram2DValidator, self).__init__("),
(8, "            plotly_name=plotly_name,"),
(9, "            parent_name=parent_name,"),
(10, "            data_class_str=kwargs.pop('data_class_str', 'Histogram2d'),"),
(11, "            data_docs=kwargs.pop("),
(12, '                "data_docs",'),
(13, '                """'),
(14, '        """,'),
(15, "            ),"),
(16, "            **kwargs,"),
(17, "        )"),
],
"utils/check_config.py": [
(31, "except FileNotFoundError:"),
(32, '    print("\\nconfig.json file not found")'),
(33, "except json.JSONDecodeError:"),
(34, '    print("\\nconfig.json is not valid JSON")'),
(35, "except Exception as e:"),
(36, '    print(f"\\nError reading config.json: {str(e)}")'),
],
"utils/env_checker.py": [
(8, "def check_env_setup():"),
(9, '    """Check if .env file exists and contains required variables"""'),
(10, "    logger = logging.getLogger(__name__)"),
(11, "    env_path = Path('.env')"),
(12, "    if not env_path.exists():"),
(13, "        logger.error('.env file not found')"),
(14, "        create_env_file()"),
(15, "        return False"),
(16, "    load_dotenv(override=True)"),
(17, "    required_vars = ['OPENAI_API_KEY']"),
(18, "    missing_vars = []"),
(19, "    for var in required_vars:"),
(20, "        if not os.getenv(var):"),
(21, "            missing_vars.append(var)"),
(22, "    if missing_vars:"),
(23, "        logger.error(f'Missing environment variables: {', '.join(missing_vars)}')"),
(24, "        return False"),
(25, "    return True"),
(26, "def create_env_file():"),
(27, '    """Create a template .env file"""'),
(28, "    template = '''# OpenAI API Key (Required)"),
(29, "    OPENAI_API_KEY=your_api_key_here"),
(30, "    # GitHub Token (Optional)"),
(31, "    GITHUB_TOKEN=your_github_token_here"),
(32, "    '''"),
(33, "    try:"),
(34, "        with open('.env', 'w') as f:"),
(35, "            f.write(template)"),
(36, "            logging.info('Created template .env file')"),
(37, "    except Exception as e:"),
(38, "        logging.error(f'Failed to create .env file: {e}')"),
],
}

def apply_fixes(file_path, fixes):
with open(file_path, "r") as file:
lines = file.readlines()

for line_num, fix in fixes:
lines[line_num - 1] = fix + "\n"

with open(file_path, "w") as file:
file.writelines(lines)

def main():
for file_path, file_fixes in fixes.items():
if os.path.exists(file_path):
apply_fixes(file_path, file_fixes)
print(f"Applied fixes to {file_path}")
else:
print(f"File not found: {file_path}")

if __name__ == "__main__":
main()