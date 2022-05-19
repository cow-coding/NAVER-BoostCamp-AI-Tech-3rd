import os
import dotenv
import numpy as np
import webbrowser

import pandas as pd

import torch

import streamlit as st
import streamlit.components.v1 as components
from scipy.sparse import csr_matrix

from model import EASE


@st.cache
def load_data():
    dotenv.load_dotenv(verbose=True)
    data = pd.read_csv(os.getenv("SM_CHANNEL_DATA") + "/train_ratings.csv")
    movie_list = pd.read_csv(os.getenv("SM_CHANNEL_DATA") + "/titles.tsv", sep="\t")
    return data, movie_list


df, movie_list = load_data()


if "movie_dict" not in st.session_state:
    st.session_state.movie_dict = {k:v for k, v in zip(movie_list['title'].values, movie_list['item'].values)}

seen_list = list()

name = st.text_input("이름을 입력해주세요!")

multi_select = st.multiselect("좋아하시는 영화를 모두 골라주세요 (제목을 영문명으로 검색하셔야 합니다. ex. matrix)",
                              st.session_state.movie_dict)


if st.button("영화 추천해 드릴게요!"):
    if len(multi_select) > 0:
        user = 200000
        time = 1258390489
        new_data = {
            "user": [],
            "item": [],
            "time": []
        }

        with st.spinner(f"{name} 님이 좋아하시는 영화를 확인중이에요!"):
            for i in range(len(multi_select)):
                new_data["user"].append(user)
                new_data["item"].append(st.session_state.movie_dict[multi_select[i]])
                new_data["time"].append(time)
                seen_list.append(st.session_state.movie_dict[multi_select[i]])

        seen_list = np.array(seen_list)
        new_df = pd.DataFrame(new_data)
        df = pd.concat([df, new_df], ignore_index=True)

        with st.spinner("영화를 추천 중 입니다... (2 ~ 3분 정도의 시간이 소요돼요)"):
            model = EASE(df)

            model.fit(0.5)

        uid = model.user2id[user]
        pred = model.pred[uid]
        rating = torch.sigmoid(torch.Tensor(pred)) * 5
        pred = np.argsort(-pred)
        pred = np.array([model.id2item[item] for item in pred])
        pred = pred[np.isin(pred, seen_list) == False]

        top_k = pred[:10]

        print(rating)

        st.write(f"{name} 님에게 추천 드리는 영화 10개에요!")

        for idx, i in enumerate(top_k):
            if idx == 0:
                st.write(f"{movie_list[movie_list['item'] == i].title.values[0]} (예상 점수 : {round(rating[idx].tolist(), 2)}) 을 가장 좋아하실 거 같군요")
            else:
                st.write(f"{movie_list[movie_list['item'] == i].title.values[0]} (예상 점수 : {round(rating[idx].tolist(), 2)})")
    else:
        st.write("영화를 1개는 골라 주세야 해요 ㅠㅠ")
