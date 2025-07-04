import re

def extract_suggestion(text):
    '''
        Next, you can:
        [1] Perform hyperparameter tuning of the random forest model to improve classification performance.
        [2] Try other classification algorithms such as SVM or neural networks to compare results.
        [3] Conduct feature importance analysis or dimensionality reduction to better understand the data.
    '''

    return re.findall(r'\[\d+\]\s*(.*)', text)

def format_suggestion(chat_history_display, suggestions):
    '''
    Replace:
        Next, you can:
        [1] Perform hyperparameter tuning of the random forest model to improve classification performance.
        [2] Try other classification algorithms such as SVM or neural networks to compare results.
        [3] Conduct feature importance analysis or dimensionality reduction to better understand the data.

    by:
        <div>
            <button class="suggestion-btn" data-bound="true">Perform hyperparameter tuning of the random forest model to improve classification performance.</button>
            <button class="suggestion-btn" data-bound="true">Try other classification algorithms such as SVM or neural networks to compare results.</button>
            <button class="suggestion-btn" data-bound="true">Conduct feature importance analysis or dimensionality reduction to better understand the data.</button>
        </div>
    '''
    # chat_history_display[-1][1].replace()
    index = chat_history_display[-1][1].find("[1]")
    if index != -1:
        chat_history_display[-1][1] = chat_history_display[-1][1][:index]
        chat_history_display[-1][1] += suggestions

