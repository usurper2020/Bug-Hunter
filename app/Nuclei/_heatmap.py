import re
import _plotly_utils.basevalidators


class HeatmapValidator(_plotly_utils.basevalidators.CompoundArrayValidator):
def __init__(self, plotly_name='heatmap', parent_name='layout.template.data', **kwargs):
super(HeatmapValidator, self).__init__(
plotly_name=plotly_name,
parent_name=parent_name,
data_class_str=kwargs.pop('data_class_str', 'Heatmap'),
data_docs=kwargs.pop(
pass
"""
""",
),
**kwargs,
)
"data_docs",
"""
""",
),
**kwargs,
)
