from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, BubbleContainer, ImageComponent, MessageAction
import logging

victimMessage = {
    "type": "text",
    "alt_text": "まず、あなた or 事故に遭われた家族について教えてください。"
}
victimFlexData = {
    "type": "flex",
    "alt_text": "まず、あなたについて教えてください。", 
    "images": ["1.PNG", "2.PNG"],
    "values": ["被害者", "加害者"],
}

accidentMessage = {
    "type": "text",
    "alt_text": "事故の状況について教えてください"
}

accidentFlexData = {
    "type": "flex",
    "alt_text": "事故の種類を教えてください",
    "images": ["3.PNG", "4.PNG","5.PNG","6.PNG"],
    "values": ["軽傷", "重症","死亡","物損のみ"]
}

injuryMessage = {
    "type": "text",
    "alt_text": "お怪我の状況について教えて下さい"
}

injuryFlexData = {
    "type": "flex",
    "alt_text": "お怪我の状況について教えて下さい",
    "images": ["7.PNG", "11.png"],
    "values": ["むちうち","その他"]
}


injuryFlexData2 = {
    "type": "flex",
    "alt_text": "お怪我の状況について教えて下さい",
    "images": ["8.PNG", "9.PNG", "10.PNG","11.png"],
    "values": ["骨折","脳障害","欠損障害","その他"]
}

treatmentMessage = {
    "type": "text",
    "alt_text": "現在の治療状況について教えてください"
}

treatmentFlexData = {
    "type": "flex",
    "alt_text": "現在の治療状況について教えてください",
    "images": ["25.png", "26.png"],
    "values": ["治療中", "治療終了"]
}

hospitalizationTermMessage = {
    "type": "text",
    "alt_text": "⼊院期間（日数）を教えてください ※数字のみ(⼊⼒例: 30)"
}

dotctorVisitTermMessage = {
    "type": "text",
    "alt_text": "通院期間を教えてください ※事故から治療終了までの⽇数（⼊⼒例：180）"
}

actualDoctorVisitTermMessage = {
    "type": "text",
    "alt_text": "実際に通院した⽇数を教えてください ※数字のみ（⼊⼒例：90）"
}

workDaysLostMessage = {
    "type": "text",
    "alt_text": "休業した⽇数を教えてください ※専業主婦の⽅は家事育児ができなかった⽇数（⼊⼒例：30）"
}

ageMessage = {
    "type": "text",
    "alt_text": "事故時の年齢を教えてください ※数字のみ（⼊⼒例：35）"
}

afftereffectMessage = {
    "type": "text",
    "alt_text": "認定されている後遺障害等級を教えてください ※⾮該当は０、等級は1〜14の数字のみ（⼊⼒例：12）"
}

familyPositionMessage = {
    "type": "text",
    "alt_text": "被害者とあなたの関係を教えてください。（一家の支柱、配偶者・母親、その他のいずれかで入力）"
}

genderMessage = {
    "type": "text",
    "alt_text": "性別を教えてください。"
}

genderFlexData = {
    "type": "flex",
    "alt_text": "性別を教えてください。",
    "images": ["12.png", "13.png"],
    "values": ["男性", "女性"]
}

relationshipMessage = {
    "type": "text",
    "alt_text": "婚姻状況を教えてください"
}

relationshipFlexData = {
    "type": "flex",
    "alt_text": "婚姻状況を教えてください",
    "images": ["14.png", "15.png"],
    "values": ["既婚", "独身"]
}

salaryAmountMessage = {
    "type": "text",
    "alt_text": "事故前の年収を教えてください ※年収は数字のみ。単位は万円。ない場合は0と入力。⼊⼒例：500）"
}

dependentsMessage = {
    "type": "text",
    "alt_text": "被扶養家族の⼈数を教えてください ※数字のみ（⼊⼒例：2）"
}

lawyerMessage = {
    "type": "text",
    "alt_text": (
            f"加入保険に弁護士費用特約の付帯はありましたか？\n"
            f"なお、弁護士費用特約の適用範囲は、契約者本人だけでなく周囲の一定範囲の加入保険も対象となります。\n"
            f"（例）\n"
            f"・被保険者の配偶者\n"
            f"・被保険者の同居の家族\n"
            f"・被保険者の別居の未婚の子\n"
            f"・被保険者の同乗者\n"
            f"・契約車両の同乗者　など\n"
            f"※その他、適用範囲がありますので弁護士にご相談ください。"
        )
}

laywerFlexData = {
    "type": "flex",
    "alt_text": "弁護士費用特約の有無を教えてください。弁特がなくても相談は無料です。",
    "images": ["18.PNG", "19.PNG","20.PNG"],
    "values": ["あり", "なし","わからない"]
}

contactMessage = {
    "type": "text",
    "alt_text": (
        f"このあと慰謝料の計算結果を表示しますので、最後に相談方法やご連絡先情報を教えてください。\n\n"
        f"まず、ご希望の相談方法を教えてください\n"
    )
}

consultationFlexData = {
    "type": "flex",
    "alt_text": "ご希望の相談方法を教えてください",
    "images": ["21.PNG", "24.PNG"],
    "values": ["来所で相談", "オンラインで相談"]
}

nameMessage = {
    "type": "text",
    "alt_text": "お名前を教えてください"
}

telMessage = {
    "type": "text",
    "alt_text": "携帯またはご自宅のお電話番号を教えてください"
}

emailMessage = {
    "type": "text",
    "alt_text": "メールアドレスを教えてください"
}

addressMessage = {
    "type": "text",
    "alt_text": "最後に、お住いの地域（市町村まで）を教えてください"
}

thanksMessage = {
    "type": "text",
    "alt_text": (
        f"ご回答ありがとうございました。今後の相談につきましては、担当者より追って連絡させていただきます。\n"
        f"また弁護士特約がない場合でも、無料相談・着手金・報酬金など弁護士費用は完全成功報酬でご依頼できますので、本LINEアカウントよりご相談ください。"
    )
}

appointmentMessage = {
    "type": "text",
    "alt_text": (
        f"ご相談のご予約ありがとうございます。\n"
        f"ご連絡先情報やご相談方法などを教えてください。\n\n"
        f"まずご希望のご相談方法を選択してください。"
    )
}

exceptionVictimMessage = {
    "type": "text",
    "alt_text": "誠に申し訳ございません。当事務所では加害者側のご相談はお受けしておりません。"
}

exceptionAccidentMessage = {
    "type": "text",
    "alt_text": "誠に申し訳ございません。当事務所では物損のみのご相談はお受けしておりません"
}
exceptionTreatmentMessage = {
    "type": "text",
    "alt_text": "適切な治療を受けるためにも弁護士へ相談しましょう。ご相談の方はメニューの「相談のご予約」をタップしてください。"
}

reply_message_metas = [
    {
        "id": 1,
        "next": 2,
        "key": "victim",
        "data": [victimMessage, victimFlexData],
        "condition_keys": ["加害者"],
        "condition_ids": [25]
    },
    {
        "id": 2,
        "next": 3,
        "key": "accidentType",
        "data": [accidentMessage, accidentFlexData],
        "condition_keys": ["重症","死亡","物損のみ"],
        "condition_ids": [4, 12, 26]
    },
    {
        "id": 3,
        "next": 5,
        "key": "injuryType",
        "data": [injuryMessage, injuryFlexData]
    },
    {
        "id": 4,
        "next": 5,
        "key": "injuryType",
        "data": [injuryMessage, injuryFlexData2]
    },
    {
        "id": 5,
        "next": 6,
        "key": "treatment",
        "data": [treatmentMessage, treatmentFlexData],
        "condition_keys": ["治療中"],
        "condition_ids": [27]
    },
    {
        "id": 6,
        "next": 7,
        "key": "hospitalizationTerm",
        "data": [hospitalizationTermMessage]
    },
    {
        "id": 7,
        "next": 8,
        "key": "doctorVisitTerm",
        "data": [dotctorVisitTermMessage]
    },
    {
        "id": 8,
        "next": 9,
        "key": "actualDoctorVisitTerm",
        "data": [actualDoctorVisitTermMessage]
    },
    {
        "id": 9,
        "next": 10,
        "key": "workDaysLost",
        "data": [workDaysLostMessage]
    },
    {
        "id": 10,
        "next": 11,
        "key": "age",
        "data": [ageMessage]
    },
    {
        "id": 11,
        "next": 14,
        "key": "aftereffect",
        "data": [afftereffectMessage]
    },
    {
        "id": 12,
        "next": 28,
        "key": "familyPosition",
        "data": [familyPositionMessage]
    },
    {
        "id": 13,
        "next": 14,
        "key": "age",
        "data": [ageMessage]
    },
    {
        "id": 14,
        "next": 15,
        "key": "gender",
        "data": [genderMessage, genderFlexData]
    },
    {
        "id": 15,
        "next": 17,
        "key": "relationship",
        "data": [relationshipMessage, relationshipFlexData]
    },
    {
        "id": 16,
        "next": 17,
        "key": "dependents",
        "data": [dependentsMessage]
    },
    {
        "id": 17,
        "next": 18,
        "key": "salaryAmount",
        "data": [salaryAmountMessage]
    },
    {
        "id": 18,
        "next": 19,
        "key": "lawyerFeeSpecialClause",
        "data": [lawyerMessage, laywerFlexData]
    },
    {
        "id": 19,
        "next": 20,
        "key": "consultation",
        "data": [contactMessage, consultationFlexData]
    },
    {
        "id": 20,
        "next": 21,
        "key": "name",
        "data": [nameMessage]
    },
    {
        "id": 21,
        "next": 22,
        "key": "tel",
        "data": [telMessage]
    },
    {
        "id": 22,
        "next": 23,
        "key": "email",
        "data": [emailMessage]
    },
    {
        "id": 23,
        "next": 24,
        "key": "address",
        "data": [addressMessage]
    },
    {
        "id": 24,
        "next": 24,
        "key": "thanks",
        "data": [thanksMessage]
    },
    {
        "id": 25,
        "next": 0,
        "key": "exception",
        "data": [exceptionVictimMessage]
    },
    {
        "id": 26,
        "next": 0,
        "key": "exception",
        "data": [exceptionAccidentMessage]
    },
    {
        "id": 27,
        "next": 0,
        "key": "exception",
        "data": [exceptionTreatmentMessage]
    },
    {
        "id": 28,
        "next": 29,
        "key": "age",
        "data": [ageMessage]
    },
    {
        "id": 29,
        "next": 30,
        "key": "gender",
        "data": [genderMessage, genderFlexData]
    },
    {
        "id": 30,
        "next": 16,
        "key": "relationship",
        "data": [relationshipMessage, relationshipFlexData]
    },
]