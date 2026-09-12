import re
from typing import List, Tuple

# 高风险敏感词黑名单库（代课、代考、刷课、刷网课、代写作业、论文代写、作弊等）
SENSITIVE_WORDS: List[str] = [
    "代课", "替课", "代上课", "代出勤",
    "刷课", "刷网课", "代刷课", "学习通代刷", "超星代刷", "知到代刷", "网课代看",
    "代考", "替考", "替考替考", "期末代考", "四六级代考",
    "代写作业", "代写论文", "写作业", "代写报告", "论文代发", "作弊", "枪手",
    "赌博", "色情", "兼职刷单", "刷单", "办假证", "套现"
]

def check_sensitive_content(text: str) -> Tuple[bool, str]:
    """
    检查文本是否包含敏感词
    :param text: 待检测文本
    :return: (is_blocked, hit_word)
    """
    if not text:
        return False, ""

    # 过滤空格和特殊标点符号进行混淆检测
    normalized_text = re.sub(r"[\s\-_，。！？\*\#\@\$\%\^\&\(\)]+", "", text).lower()

    for word in SENSITIVE_WORDS:
        if word in text or word in normalized_text:
            return True, word

    return False, ""
