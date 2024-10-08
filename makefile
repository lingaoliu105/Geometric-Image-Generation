GEN_NUM = 10

# latex源文件目录
SRC_DIR = output_tex

# pdf目标文件目录
OBJ_DIR = output_pdf

# png图片输出目录
TARGET_DIR = output_png

# json文件输出目录
JSON_DIR = output_json

DATASET_DIR=  my_dataset

SRCS = $(wildcard $(SRC_DIR)/*.tex)

OBJS = $(SRCS:$(SRC_DIR)/%.tex=$(OBJ_DIR)/%.pdf)

TARGETS = $(OBJS:$(OBJ_DIR)/%.pdf=$(TARGET_DIR)/%.png)

# 默认目标
all: dir tex pdf png labels

dir:
	mkdir -p $(OBJ_DIR)
	mkdir -p $(SRC_DIR)
	mkdir -p $(TARGET_DIR)
	mkdir -p $(JSON_DIR)

tex: dir gen_rand_tikz.py
	python gen_rand_tikz.py $(GEN_NUM)

$(OBJ_DIR)/%.pdf : $(SRC_DIR)/%.tex
	pdflatex -interaction=batchmode -output-directory=$(OBJ_DIR) $<

pdf: $(OBJS)

$(TARGET_DIR)/%.png : $(OBJ_DIR)/%.pdf
	python convert_image.py $<

png: $(TARGETS)
	cp $(TARGET_DIR)/* $(DATASET_DIR)/data

labels:
	python combine_json.py $(GEN_NUM)

show:
	python dataset_visualization.py

# 清理生成的文件
clean:
	rm -f $(SRC_DIR)/* $(OBJ_DIR)/* $(TARGET_DIR)/* $(JSON_DIR)/*

# PHONY 目标表示这些目标不是实际文件
.PHONY: all clean