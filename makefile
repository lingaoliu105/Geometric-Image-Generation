GEN_NUM = 10

GEN_FILE_PREFIX = new-

COLOR_MODE = colored

# latex源文件目录
TEX_DIR = output_tex/

# pdf目标文件目录
PDF_DIR = output_pdf/

# png图片输出目录
PNG_DIR = output_png/

# json文件输出目录
JSON_DIR = output_json/

DATASET_DIR=  my_dataset/

NUMS = $(shell seq 0 $(shell expr $(GEN_NUM) - 1))
TEX_FILES = $(foreach n,$(NUMS),$(TEX_DIR)/$(GEN_FILE_PREFIX)$(n).tex)
PDF_FILES = $(foreach n,$(NUMS),$(PDF_DIR)/$(GEN_FILE_PREFIX)$(n).pdf)
PNG_FILES = $(foreach n,$(NUMS),$(PNG_DIR)/$(GEN_FILE_PREFIX)$(n).png)

IS_CONTAINER := $(shell grep -i docker /proc/self/cgroup > /dev/null && echo "true" || echo "false")

.PHONY: all clean png

all: clean tex pdf png dataset

png: $(PNG_FILES)

$(PDF_DIR):
	@mkdir -p $(PDF_DIR)

$(TEX_DIR):
	@mkdir -p $(TEX_DIR)

$(PNG_DIR):
	@mkdir -p $(PNG_DIR)

$(JSON_DIR):
	@mkdir -p $(JSON_DIR)

$(DATASET_DIR):
	@mkdir -p $(DATASET_DIR)

tex: | $(TEX_DIR) $(JSON_DIR)
	python -W ignore gen_rand_tikz.py $(GEN_NUM) $(COLOR_MODE) $(GEN_FILE_PREFIX)

$(PDF_DIR)%.pdf : $(TEX_DIR)%.tex | $(PDF_DIR)
	pdflatex -interaction=batchmode -output-directory=$(PDF_DIR) $<
	
pdf: $(PDF_FILES)
	@# @if [ "$(IS_CONTAINER)" = "false" ]; then \
	# 	echo "Running in WSL environment."; \
	# 	docker-compose up; \
	# else \
	# 	echo "Not running in WSL environment."; \
	# fi


$(PNG_DIR)%.png : $(PDF_DIR)%.pdf | $(PNG_DIR)
	python convert_image.py $<

dataset: | $(DATASET_DIR)
	python combine_json.py $(GEN_NUM) $(GEN_FILE_PREFIX)
	@mkdir -p $(DATASET_DIR)data
	cp $(PNG_DIR)* $(DATASET_DIR)data

show:
	python dataset_visualization.py

# 清理生成的文件
clean:
	@rm -rf $(TEX_DIR)* $(PDF_DIR)* $(PNG_DIR)* $(JSON_DIR)* $(DATASET_DIR)*
