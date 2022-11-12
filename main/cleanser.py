from main.model.text_processing import Abusive, KamusAlay
import numpy as np
import re


emoticons_happy = [
    ':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
    ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
    '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
    'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)',
    '<3'
    ]
emoticons_sad = [
    ':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
    ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
    ':c', ':{', '>:\\', ';('
    ]

def bersihkan_tweet(tweet):
    # cek apakah string ataukah afloat
    if type(tweet) == np.float:
        return ""
    # emoticons list
    emoticons = emoticons_happy + emoticons_sad
    # adding text need to remove
    emoticons.append("http")
    emoticons.append("url")

    # list dari pattern emoji
    EMOJI_PATTERN = re.compile(
        "["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+"
        , flags=re.UNICODE)

    # menghapus spesial karakter diakhir string karena error UnicodeDecodeError: 'unicodeescape' codec can't decode byte 0x5c in position 209: \ at end of string
    # temp = re.sub(f"[ ,;:/]*$", " ", tweet)

    # hapus karakter yang dimulai dengan \x (gak jadi pake. karena kalo nempel kata dibelakang jadi kehapus)
    # temp = re.sub("\\\\x[a-z0-9_]+", " ", temp)

    try:
        # sub karakter \n
        temp = re.sub(f"\\\\n", " ", tweet)
        # ubah ke utf, ganti \\ dengan \ lalu ganti \u dengan \u000 lalu balikan ke unicode_escape
        temp = temp.encode(
            'unicode_escape').decode('utf-8').replace('\\\\', '\\').replace('\\u', '\\U000').encode('latin-1').decode('unicode-escape')
    except:
        # jika error karena UnicodeDecodeError: 'unicodeescape' codec can't decode byte 0x5c in position 209: \ at end of string
        # split ke kata2
        array_split = tweet.split()
        # hapus kata terakhir dengan harapan tak ada lagi unicodeescape
        temp = tweet.replace(array_split[-1], " ")
        # sub karakter \n
        temp = re.sub(f"\\\\n", " ", temp)
        # ubah ke utf, ganti \\ dengan \ lalu ganti \u dengan \u000 lalu balikan ke unicode_escape
        temp = temp.encode(
            'unicode_escape').decode('utf-8').replace('\\\\', '\\').replace('\\u', '\\U000').encode('latin-1').decode(
            'unicode-escape')

    # merubah patern emoji
    temp = EMOJI_PATTERN.sub(r'', temp)
    # hapus mention @
    temp = re.sub("@[A-Za-z0-9_]+","", temp)
    # hapus hashtag
    # temp = re.sub("#[A-Za-z0-9_]+","", temp) kayaknya gak perlu
    #hapus tanda baca ()!?
    temp = re.sub('[()!?]', ' ', temp)
    # hapus karakter yang tidak dalam range a-z0-9x (karena emojinya udah jadi bentuk, bukan huruf, emoji bisa tersingkir)
    temp = re.sub("[^A-Za-z0-9]"," ", temp)
    # lowercase huruf
    temp = temp.lower()
    # # hapus kata duplikasi yang berurutan
    temp = re.sub(r'\b(\w+)( \1\b)+', r'\1', temp)
    #unjoin karakter untuk nantinya dijoin agar single spasi
    temparray = temp.split()
    filtered_tweet = []
    for w in temparray:
        if w not in emoticons and w.upper() not in emoticons:
            filtered_tweet.append(cek_alay_dan_abuse(w))
    temp = " ".join(word for word in filtered_tweet)
    return temp


def cek_alay_dan_abuse(w):
    alay = KamusAlay.query.filter(KamusAlay.word == w).first()
    if alay:
        # print(alay.Abusive)
        if Abusive.query.filter(Abusive.word == alay.meaning).first():
            return "X"*len(w)
        return alay.meaning
    else:
        abusive = Abusive.query.filter(Abusive.word == w).first()
        if abusive:
            return "X" * len(w)
    return w