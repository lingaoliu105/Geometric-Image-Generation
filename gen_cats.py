import json


sup_to_cat = {
    "Type": [
        "dot",
        "linesegment",
        "triangle",
        "square",
        "rectangle",
        "pentagon",
        "hexagon",
        "heptagon",
        "octagon",
        "nonagon",
        "decagon",
        "circle",
        "ellipse",
        "star",
        "diamond",
        "arrow",
        "doublearrow",
        "arc",
        "intersectionDot",
        "intersectionLineSegment",
        "intersectionArc",
        "intersectionRegion",
    ],
    "Size": [
        "tiny",
        "nearTiny",
        "small",
        "slightlySmaller",
        "normalSize",
        "slightlyLarger",
        "large",
        "nearHuge",
        "huge",
    ],
    "HorizontalPosition0": [
        "left",
        "nearLeft",
        "leftwards",
        "slightlyLeftwards",
        "horizontalMiddle",
        "slightlyRightwards",
        "rightwards",
        "nearRight",
        "right",
    ],
    "VerticalPosition": [
        "top",
        "nearTop",
        "high",
        "slightlyHigher",
        "verticalMiddle",
        "slightlyLower",
        "low",
        "nearBottom",
        "bottom",
    ],
    "Angle": [
        "deg0",
        "deg15",
        "deg30",
        "deg45",
        "deg60",
        "deg75",
        "deg90",
        "deg105",
        "deg120",
        "deg135",
        "deg150",
        "deg165",
        "deg180",
        "degMinus15",
        "degMinus30",
        "degMinus45",
        "degMinus60",
        "degMinus75",
        "degMinus90",
        "degMinus105",
        "degMinus120",
        "degMinus135",
        "degMinus150",
        "degMinus165",
    ],
    "Color": [
        "white",
        "black",
        "red",
        "green",
        "blue",
        "cyan",
        "magenta",
        "yellow",
        "purple",
        "brown",
        "orange",
    ],
    "Lightness": [
        "lightness20",
        "lightness25",
        "lightness33",
        "lightness40",
        "lightness50",
        "lightness60",
        "lightness67",
        "lightness75",
        "lightness80",
        "lightness100",
    ],
    "Pattern": [
        "blank",
        "horizontalLines",
        "verticalLines",
        "northeastLines",
        "northwestLines",
        "grid",
        "crosshatch",
        "dots",
        "crosshatchDots",
        "fivepointedStars",
        "sixpointedStars",
        "bricks",
        "checkerboard",
    ],
    "PatternColor": [
        "patternWhite",
        "patternBlack",
        "patternRed",
        "patternGreen",
        "patternBlue",
        "patternCyan",
        "patternMagenta",
        "patternYellow",
        "patternPurple",
        "patternBrown",
        "patternOrange",
    ],
    "PatternLightness": [
        "patternLightness20",
        "patternLightness25",
        "patternLightness33",
        "patternLightness40",
        "patternLightness50",
        "patternLightness60",
        "patternLightness67",
        "patternLightness75",
        "patternLightness80",
        "patternLightness100",
    ],
    "Outline": [
        "solid",
        "dotted",
        "denselyDotted",
        "looselyDotted",
        "dashed",
        "denselyDashed",
        "looselyDashed",
        "dashdotted",
        "denselyDashdotted",
        "dashdotdotted",
        "denselydashdotdotted",
        "looselydashdotdotted",
    ],
    "OutlineThickness": [
        "noOutline",
        "ultraThin",
        "veryThin",
        "thin",
        "semithick",
        "thick",
        "veryThick",
        "ultraThick",
    ],
    "OutlineColor": [
        "outlineWhite",
        "outlineBlack",
        "outlineRed",
        "outlineGreen",
        "outlineBlue",
        "outlineCyan",
        "outlineMagenta",
        "outlineYellow",
        "outlinePurple",
        "outlineBrown",
        "outlineOrange",
    ],
    "OutlineLightness": [
        "outlineLightness20",
        "outlineLightness25",
        "outlineLightness33",
        "outlineLightness40",
        "outlineLightness50",
        "outlineLightness60",
        "outlineLightness67",
        "outlineLightness75",
        "outlineLightness80",
        "outlineLightness100",
    ],
    "RelativeOrder": [
        "first",
        "second",
        "third",
        "fourth",
        "fifth",
        "sixth",
        "seventh",
        "eighth",
        "ninth",
        "tenth",
        "eleventh",
        "twelfth",
    ],
}

skeletons = {
    "triangle": {
        "keypoints": ["center", "p1", "p2", "p3"],
        "skeleton": [[1, 2], [1, 3], [1, 4]],
    },
    "square": {
        "keypoints": ["center", "p1", "p2", "p3", "p4"],
        "skeleton": [[1, 2], [1, 3], [1, 4], [1, 5]],
    },
    "rectangle": {
        "keypoints": ["center", "p1", "p2", "p3", "p4"],
        "skeleton": [[1, 2], [1, 3], [1, 4], [1, 5]],
    },
    "pentagon": {
        "keypoints": ["center", "p1", "p2", "p3", "p4", "p5"],
        "skeleton": [[1, 2], [1, 3], [1, 4], [1, 5], [1, 6]],
    },
    "hexagon": {
        "keypoints": ["center", "p1", "p2", "p3", "p4", "p5", "p6"],
        "skeleton": [[1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7]],
    },
    "heptagon": {
        "keypoints": ["center", "p1", "p2", "p3", "p4", "p5", "p6", "p7"],
        "skeleton": [[1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8]],
    },
    "octagon": {
        "keypoints": ["center", "p1", "p2", "p3", "p4", "p5", "p6", "p7"],
        "skeleton": [[1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8]],
    },
    "nonagon": {
        "keypoints": ["center", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"],
        "skeleton": [[1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7], [1, 8], [1, 9]],
    },
    "decagon": {
        "keypoints": ["center", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9"],
        "skeleton": [
            [1, 2],
            [1, 3],
            [1, 4],
            [1, 5],
            [1, 6],
            [1, 7],
            [1, 8],
            [1, 9],
            [1, 10],
        ],
    },
}

cats_list = []
get_category_id = (x for x in range(10000)).__next__
for supcat in sup_to_cat:
    cats = sup_to_cat[supcat]
    for cat_name in cats:
        cat_obj = {"id": get_category_id(), "name": cat_name, "supercategory": supcat}
        if cat_name in skeletons:
            cat_obj |= skeletons[cat_name]  # merge dicts
        cats_list.append(cat_obj)
with open("./categories.json", "w") as j:
    json.dump(cats_list, j, indent=4)
