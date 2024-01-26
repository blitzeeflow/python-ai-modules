import os
os.environ['TRANSFORMERS_CACHE'] = 'E:\model'
from transformers import pipeline


summarizer = pipeline("summarization", model="Falconsai/text_summarization")

ARTICLE = """ 
Artificial intelligence may be coming for many people's jobs according to some Fortune 500 CEOs and Silicon Valley leaders - but AI computer vision technologies are not yet cheap enough to make them worthwhile for most US businesses today. The finding comes from a study of human work - specifically tasks involving vision - that is exposed to the risk of machine automation.

In the study, researchers focused on whether vision tasks included in various human jobs are economically worth replacing using existing AI computer vision. “There are lots of tasks that you can imagine AI applying to, but actually cost-wise you just wouldn't want to do it,” says Neil Thompson at the Massachusetts Institute of Technology, co-author of the study, which was published today as a working paper.

Thompson and his colleagues identified 414 vision tasks in US job categories that could potentially be automated by existing AI technology. These jobs included retail store supervisors who visually check on whether items have the right price tags attached, and nurse anaesthesiologists who are trained to watch the patients in their care for dilated pupils or changes in cheek colour that might be warning signs of potential problems.

The researchers calculated the costs of training and operating an AI computer vision model capable of handling those tasks with the required accuracy. They then compared AI costs with the costs of human labour - the latter represented as share of total worker salaries and benefits, because vision tasks typically make up a small portion of any given employee's work duties.

They found that, although 36 per cent of US non-agricultural businesses have at least one worker task that could be automated through AI computer vision, just 8 per cent have a task that is cost-effective to automate using AI.
"""
print(summarizer(ARTICLE, max_length=230, min_length=30, do_sample=False)['summary_text'])


script_name.main("Your text here", "output.mp3", True, "E:/model_cache")