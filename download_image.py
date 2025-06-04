import json
import urllib.request

with open("./coco_dataset/example/labels.json","r") as l:
    labels = json.load(l)

import asyncio
import os

import aiohttp


async def download_image(session, url, file_name):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                with open(file_name, "wb") as file:
                    file.write(await response.read())
                print(f"Image successfully downloaded: {file_name}")
            else:
                print(
                    f"Failed to retrieve image {file_name}. Status code: {response.status}"
                )
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")


async def download_images_concurrently(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, url in enumerate(urls):
            file_name = "./coco_dataset/example/data/" + url.split("/")[-1]
            tasks.append(download_image(session, url, file_name))
        await asyncio.gather(*tasks)


# 示例：要下载的图片 URL 列表
urls = [image_object["coco_url"] for image_object in labels["images"] if not os.path.exists("./coco_dataset/example/data/"+image_object["file_name"])]

# 开始异步下载
asyncio.run(download_images_concurrently(urls))
