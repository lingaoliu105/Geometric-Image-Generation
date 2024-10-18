GEN_NUM = 10

COLOR_MODE = colored

# latex源文件目录
TEX_DIR = output_tex

# pdf目标文件目录
PDF_DIR = output_pdf

# png图片输出目录
PNG_DIR = output_png

# json文件输出目录
JSON_DIR = output_json

DATASET_DIR=  my_dataset

TEXES = $(wildcard $(TEX_DIR)/*.tex)

PDFS = $(TEXES:$(TEX_DIR)/%.tex=$(PDF_DIR)/%.pdf)

PNGS = $(PDFS:$(PDF_DIR)/%.pdf=$(PNG_DIR)/%.png)

IS_CONTAINER := $(shell grep -i docker /proc/self/cgroup > /dev/null && echo "true" || echo "false")


# 默认目标
all: dir tex pdf png labels

dir:
	mkdir -p $(PDF_DIR)
	mkdir -p $(TEX_DIR)
	mkdir -p $(PNG_DIR)
	mkdir -p $(JSON_DIR)

tex: dir gen_rand_tikz.py
	python gen_rand_tikz.py $(GEN_NUM) $(COLOR_MODE)

$(PDF_DIR)/%.pdf : $(TEX_DIR)/%.tex

	@if [ "$(IS_CONTAINER)" = "true" ]; then pdflatex -interaction=batchmode -output-directory=$(PDF_DIR) $< ; fi
	

pdf: $(PDFS)
	@if [ "$(IS_CONTAINER)" = "false" ]; then \
		echo "Running in WSL environment."; \
		docker-compose up; \
	else \
		echo "Not running in WSL environment."; \
	fi


$(PNG_DIR)/%.png : $(PDF_DIR)/%.pdf
	echo "convert"
	python convert_image.py $<

png: $(TARGETS)
	cp $(PNG_DIR)/* $(DATASET_DIR)/data

labels:
	python combine_json.py $(GEN_NUM)

show:
	python dataset_visualization.py

# 清理生成的文件
clean:
	rm -f $(TEX_DIR)/* $(PDF_DIR)/* $(PNG_DIR)/* $(JSON_DIR)/*

# PHONY 目标表示这些目标不是实际文件
.PHONY: all clean $(PNGS)