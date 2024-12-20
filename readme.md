### Input Format

User input shall be given in a json file (`/input.json`). Supported fields are:

1. `color_mode`, which represents the images should be colored or in black and white.
     Supported options are:
     1. `mono`: the images are black and white
     2. ` colored`: the images are colored

2. `canvas_width`: The width of the canvas. Default `20.0`

3. `canvas_height`: The height of the canvas. Default `20.0`

4. `layout`: The layout of the panels, given in the form of a 2-entry array.

      > Example:
      >
      > ```json
      > {
      > ...,
      > "layout":[2,2],
      > // The image will have 4 panels, 2 columns and 2 rows
      > }
      > ```
      >
      > 

5. `generated_file_prefix`: the prefix of the generated files' names.

6. `composition_type`: how the individual elements on a single panel are composed.

   1. `chain`: the elements are organized in  a  chain
   2. `random`: the elements are randomly placed on the panel
   3. `radial`: several elements surrounding a central element
   4. `simple`: only one element is generated on the panel
   5. `enclosing`: will generate an enclosing image on panel

7. `sub_composition_distribution`: an json object of above options from `composition_type` as keys, and their frequencies (represented in floating numbers) as the values. This object will be used to choose how each element is generated under the rule of `composition_type`.

      > Example:
      >
      > ```json
      > {
      >     "composition_type": "random",
      >     "sub_composition_distribution":{"simple":0.5,"chain":0.5},
      >     // The top-level generation rule is random, while each sub-element have 0.5/	probability to be simple shapes or 0.5 probability to be chaining images
      > }
      > ```
      >
      > 

8. `color_distribution`: a list of floats of length 11, each number represents the probability of choosing the specific color as the filling color of the elements. The list of numbers should add up to 1. The mapping of each index and color is as follows:

      | Index | Color   |
      | ----- | ------- |
      | 0     | white   |
      | 1     | black   |
      | 2     | red     |
      | 3     | green   |
      | 4     | blue    |
      | 5     | cyan    |
      | 6     | magenta |
      | 7     | yellow  |
      | 8     | purple  |
      | 9     | brown   |
      | 10    | orange  |

      > Example:
      >
      > ```json
      > {
      > ...,
      > "color_distribution":[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1] 
      > // The colors are evenly distributed, each with 0.1 probability
      > }
      > ```

9. `chaining_image_config`: an individual json object. Only works when `composition_type` is `chain`. The structure is as follows:

      | Field Name      | Accepted Values                    | Meaning                                                      |
      | --------------- | ---------------------------------- | ------------------------------------------------------------ |
      | `"draw_chain"`  | `True` or `False`                  | whether to draw or hide the chain (string)                   |
      | `"chain_shape"` | `"line"`, `"bezier"` or `"circle"` | the shape of the internal chain                              |
      | `"interval"`    | a float around 0                   | The interval between 2 adjacent elements. A positive interval means there's a distance, 0 interval means the shapes touches each other. Negative interval means overlap |
      | `"element_num"` | a positive integer                 | The number of elements on the chaining string                |

10. `random_image_config`: an individual json object. Only works when `composition_type` is `random`. The structure is as follows:

      | Field Name         | Accepted Values         | Meaning                                                      |
      | ------------------ | ----------------------- | ------------------------------------------------------------ |
      | `"centralization"` | a float between 0 and 1 | a parameter that allows elements' position closer to the center to produce more overlaps. 0 means no tuning. 1 means all elements will be shifted to the center. |
      | `"element_num"`    | a positive integer      | The number of elements on the chaining string                |

11. `radial_image_config`: an individual json object. Only works when `composition_type` is `radial`. The structure is as follows:

       | Field Name | Accepted Values | Meaning |
       | ---------- | --------------- | ------- |
       | TBD        | TBD             | TBD     |

12. `shape_distribution`: an array that specifies the probability of shape occurrence. The details are as follows:

       | Index | Shape        |
       | ----- | ------------ |
       | 0     | line segment |
       | 1     | circle       |
       | 2     | triangle     |
       | 3     | square       |
       | 4     | pentagon     |
       | 5     | hexagon      |

       





### Output Format

The generated images will be stored in `/my_dataset`, together with `label.json` which contains data annotations to the images, following COCO format.

