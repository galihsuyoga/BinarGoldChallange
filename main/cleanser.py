__author__ = 'GalihSuyoga'

from main.model.text_processing import Abusive, KamusAlay, TextLog, AlayAbusiveLog, FileTextLog, AlayAbusiveFileLog
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
emoticons = emoticons_happy + emoticons_sad
# adding text need to remove
emoticons.append("http")
emoticons.append("url")


def bersihkan_tweet_dari_text(tweet):
    # clean text rawnya
    temp = clean_text(tweet)
    # unjoin karakter untuk nantinya dijoin agar single spasi
    temparray = temp.split()
    filtered_tweet = []
    # simpan textnya dulu supaya dapat id lognya
    new_text = TextLog(text=tweet, clean=temp)
    new_text.save()
    # iterasi kalimat yang sudah displit
    for w in temparray:
        if w not in emoticons and w.upper() not in emoticons:
            # cek pake filter db dan masukkan ke parameter
            filtered_tweet.append(cek_alay_dan_abuse_db(w=w, text_id=new_text.id, full={}))
    temp = " ".join(word for word in filtered_tweet)
    # memasukkan nilai bersihnya ke objek yang telah dibuat
    new_text.clean = temp
    new_text.save()
    return temp


def bersihkan_tweet_dari_file(tweet, df_alay, df_abusive, full):
    temp = clean_text(tweet)
    # print(full)
    #unjoin karakter untuk nantinya dijoin agar single spasi
    temparray = temp.split()
    filtered_tweet = []
    # search for duplicate tweet. duplicate text input is still processed coz we didn't know if there is added knowledge
    # abusive or alay
    duplicate = FileTextLog.query.filter(FileTextLog.Tweet == tweet).first()
    if duplicate is None:
        new_text = FileTextLog(text=tweet, clean=temp, full=full)
        new_text.save()
    else:
        new_text = duplicate

    for w in temparray:
        if w not in emoticons and w.upper() not in emoticons:
            # cek pake filter pandas
            filtered_tweet.append(cek_alay_dan_abuse(w, df_alay=df_alay, df_abuse=df_abusive, text_id=new_text.ID,
                                                     full=full))
    temp = " ".join(word for word in filtered_tweet)
    new_text.Clean = temp
    new_text.save()

    return temp


def clean_text(text):
    # cek apakah string ataukah afloat
    if type(text) == np.float:
        return ""
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
        temp = re.sub(f"\\\\n", " ", text)
        # ubah ke utf, ganti \\ dengan \ lalu ganti \u dengan \u000 lalu balikan ke unicode_escape
        temp = temp.encode(
            'unicode_escape').decode('utf-8').replace('\\\\', '\\').replace('\\u', '\\U000').encode('latin-1').decode(
            'unicode-escape')
    except:

        # jika error karena UnicodeDecodeError: 'unicodeescape' codec can't decode byte 0x5c in position 209: \ at end of string
        # split ke kata2
        array_split = text.split()
        # hapus kata atau simbol byte terakhir dengan harapan tak ada lagi unicodeescape
        temp = text.replace(array_split[-1], " ")
        # sub karakter \n
        temp = re.sub(f"\\\\n", " ", temp)
        # ubah ke utf, ganti \\ dengan \ lalu ganti \u dengan \u000 lalu balikan ke unicode_escape
        temp = temp.encode(
            'unicode_escape').decode('utf-8').replace('\\\\', '\\').replace('\\u', '\\U000').encode('latin-1').decode(
            'unicode-escape')

    # merubah byte patern emoji jadi emoji
    temp = EMOJI_PATTERN.sub(r'', temp)

    # hapus mention @
    temp = re.sub("@[A-Za-z0-9_]+", "", temp)
    # hapus hashtag
    # temp = re.sub("#[A-Za-z0-9_]+","", temp) kayaknya gak perlu
    # hapus amp
    temp = re.sub("&amp"," ", temp)
    # hapus tanda baca ()!?
    temp = re.sub('[()!?]', ' ', temp)
    # hapus karakter yang tidak dalam range a-z0-9x (karena emojinya udah jadi bentuk, bukan huruf, emoji bisa tersingkir)
    temp = re.sub("[^A-Za-z0-9]", " ", temp)
    # lowercase huruf
    temp = temp.lower()
    # # hapus kata duplikasi yang berurutan
    temp = re.sub(r'\b(\w+)( \1\b)+', r'\1', temp)

    return temp


def cek_alay_dan_abuse(w, df_abuse, df_alay, text_id, full):
    #cleansing using pandas
    alay = df_alay[df_alay['word'].isin([w])]

    if len(alay) > 0:
        # print(alay.Abusive)
        meaning = list(alay['meaning'])[0]
        # check if meaning is abusive word
        abuse = df_abuse[df_abuse['word'].isin([meaning])]

        if len(abuse) > 0:
            # if abuse
            alay_abusive_log_save(text=w, clean=meaning, word_type=3, text_id=text_id, full=full)
            return "X"*len(w)
        # if not
        alay_abusive_log_save(text=w, clean=meaning, word_type=2, text_id=text_id, full=full)
        return meaning

    # if not alay
    abusive = df_abuse[df_abuse['word'].isin([w])]
    if len(abusive) > 0:
        # if abusive
        alay_abusive_log_save(text=w, clean=w, word_type=1, text_id=text_id, full=full)
        return "X" * len(w)
    return w


def cek_alay_dan_abuse_db(w, text_id, full) -> str:
    # cleansing query by db
    alay = KamusAlay.query.filter(KamusAlay.word == w).first()

    if alay:
        # check if meaning is abusive word
        abuse = Abusive.query.filter(Abusive.word == alay.meaning).first()

        if abuse:
            # if abuse saving alay abuse words
            alay_abusive_log_save(text=w, clean=alay.meaning, word_type=3, text_id=text_id, full=full)

            return "X" * len(w)
        # if not saving alay word
        alay_abusive_log_save(text=w, clean=alay.meaning, word_type=2, text_id=text_id, full=full)

        return alay.meaning

    # if not alay
    abusive = Abusive.query.filter(Abusive.word == w).first()
    if abusive:
        # if abusive
        alay_abusive_log_save(text=w, clean=w, word_type=1, text_id=text_id, full=full)

        return "X" * len(w)
    return w


def alay_abusive_log_save(text, clean, word_type, text_id, full):

    if word_type == 1:
        # abusive
        word_string = AlayAbusiveLog.foul_type_abusive()

    elif word_type == 2:
        # alay
        word_string = AlayAbusiveLog.foul_type_alay()
    else:
        # mixed
        word_string = AlayAbusiveLog.foul_type_mixed()
        # abuse = Abusive.query.filter(Abusive.word == clean).first()

    # masukkan kalimat bertipe alay, abuse atau keduanya dalam log
    if "Abusive" in full:

        exist = AlayAbusiveFileLog.query.filter(AlayAbusiveFileLog.id == text_id, AlayAbusiveFileLog.word==word_string).first()
        if exist is None:
            new_log = AlayAbusiveFileLog(word=text, clean=clean, foul_type=word_string, log_id=text_id)
            new_log.save()
    else:
        new_log = AlayAbusiveLog(word=text, clean=clean, foul_type=word_string, log_id=text_id)
        new_log.save()
