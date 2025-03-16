import os

# Define the fixes for each file
fixes = {
"Nuclei/nuclei_analyzer.py": [
(10, "    def analyze(self, data):"),
],
"Nuclei/qtpng.py": [
(10, "        pass"),
],
"Nuclei/qualitative.py": [
(17, "        pass"),
],
"Nuclei/test_cython_templating.py": [
(27, "        pass"),
],
"Nuclei/test_doc.py": [
(31, "        pass"),
],
"Nuclei/validators.py": [
(4, "        pass"),
],
"Nuclei/viewstate.py": [
(27, "        pass"),
],
"Nuclei/_bar.py": [
(19, "        pass"),
],
"Nuclei/_barpolar.py": [
(12, "        pass"),
],
"Nuclei/_candlestick.py": [
(12, "        pass"),
],
"Nuclei/_choropleth.py": [
(12, "        pass"),
],
"Nuclei/_choroplethmap.py": [
(12, "        pass"),
],
"Nuclei/_choroplethmapbox.py": [
(15, "        pass"),
],
"Nuclei/_completion_classes.py": [
(11, "        pass"),
],
"Nuclei/_cone.py": [
(12, "        pass"),
],
"Nuclei/_contourcarpet.py": [
(12, "        pass"),
],
"Nuclei/_densitymap.py": [
(12, "        pass"),
],
"Nuclei/_densitymapbox.py": [
(12, "        pass"),
],
"Nuclei/_dimensions.py": [
(59, "        pass"),
],
"Nuclei/_funnel.py": [
(12, "        pass"),
],
"Nuclei/_funnelarea.py": [
(12, "        pass"),
],
"Nuclei/_gauge.py": [
(50, "        pass"),
],
"Nuclei/_heatmap.py": [
(12, "        pass"),
],
"Nuclei/_heatmapgl.py": [
(12, "        pass"),
],
"Nuclei/_histogram.py": [
(12, "        pass"),
],
"Nuclei/_histogram2d.py": [
(12, "        pass"),
],
"Nuclei/_histogram2dcontour.py": [
(15, "        pass"),
],
"Nuclei/_hovertemplate.py": [
(17, "        pass"),
],
"Nuclei/_hovertemplatesrc.py": [
(13, "        pass"),
],
"Nuclei/_icicle.py": [
(12, "        pass"),
],
"Nuclei/_image.py": [
(12, "        pass"),
],
"Nuclei/_indicator.py": [
(12, "        pass"),
],
"Nuclei/_isosurface.py": [
(13, "        pass"),
],
"Nuclei/_layout.py": [
(19, "        pass"),
],
"Nuclei/_mesh3d.py": [
(12, "        pass"),
],
"Nuclei/_ohlc.py": [
(12, "        pass"),
],
"Nuclei/_parcats.py": [
(12, "        pass"),
],
"Nuclei/_parcoords.py": [
(12, "        pass"),
],
"Nuclei/_pie.py": [
(19, "        pass"),
],
"Nuclei/_pointcloud.py": [
(12, "        pass"),
],
"Nuclei/_rangebreaks.py": [
(73, "        pass"),
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