from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import List

import pandas as pd
import requests
import streamlit as st
from lxml import html

from constants import *

# @dataclass
# class Contribution:
#     __slots__ = ("order_id", "contributor", "contribution_date", "project_id", "contribution", "certificate")
#     order_id: int
#     contributor: str
#     contribution_date: datetime
#     project_id: List[int]
#     contribution: float
#     certificate: str
# Contribution = namedtuple(
#     "Contribution",
#     "order_id contributor contribution_date project_id contribution certificate"
# )


@st.experimental_memo(ttl=20)
def contribution_metrics():

    results = requests.get(CONTRIBUTION_HISTORY_BASE_URL).text
    tree = html.fromstring(results)
    # query_job = client.query(query)
    # rows_raw = query_job.result()
    # # Convert to list of dicts. Required for st.experimental_memo to hash the return value.
    # df = pd.DataFrame([dict(row) for row in rows_raw])
    # return df
    return [
        float(tree.xpath(selector)[0].split(": ")[-1].replace(",", ""))
        for selector in CONTRIBUTION_METRIC_XPATHS
    ]


def parse_card(div):
    return dict(
        order_id=int(div.xpath("div/div/a")[0].get("href").split("=")[-1]),
        contributor=div.xpath("div/div/b/text()")[0],
        contribution_date=datetime.strptime(
            div.xpath("div/div[2]/text()")[0], "%d %B %Y"
        ),
        project_id=[
            int(id)
            for id in div.xpath("div/div[3]/text()")[0].split(": ")[-1].split("; ")
        ],
        contribution=float(
            div.xpath("div/div[4]/text()")[0].split(" ")[0].replace(",", "")
        ),
        certificate=div.xpath("div/div[5]/text()")[0].split(": ")[-1],
    )


@st.cache
def project_info(project_id):

    results = requests.get(PROJECT_INFO_QUERY_URL.format(project_id=project_id)).text
    tree = html.fromstring(results)

    registration_date = datetime.strptime(
        tree.xpath(PROJECT_INFO_REGISTRATION_DATE_XPATH)[0], "%d %b %y"
    )
    project_name = tree.xpath(PROJECT_INFO_PROJECT_XPATH)[0]
    project_url = project_name.get("href")
    project_name = project_name.text

    return registration_date, project_url, project_name


# @st.experimental_memo(ttl=20)
@st.cache
def contribution_history(project_id):

    contributions = []

    # get the first page to know what is the last page
    results = requests.get(
        CONTRIBUTION_REDIRECT_URL.format(project_id=project_id, page=1)
    ).text
    tree = html.fromstring(results)

    # get the last page number
    pagination = tree.xpath(CONTRIBUTION_HISTORY_PAGINATION_XPATH)
    if len(pagination) == 0:
        last_page = 2
    elif pagination[-1].text != "Last":
        last_page = int(pagination[-2].get("href").split("pageNumber=")[-1])
    else:
        last_page = int(pagination[-1].get("href").split("pageNumber=")[-1])

    # get cards of the first page
    for card in tree.xpath(CONTRIBUTION_CARD_XPATH):
        con = parse_card(card)
        if project_id in con["project_id"]:
            contributions.append(con)

    for i in range(2, last_page + 1):
        results = requests.get(
            CONTRIBUTION_REDIRECT_URL.format(project_id=project_id, page=i)
        ).text
        tree = html.fromstring(results)
        for card in tree.xpath(CONTRIBUTION_CARD_XPATH):
            con = parse_card(card)
            if project_id in con["project_id"]:
                contributions.append(con)
    # query_job = client.query(query)
    # rows_raw = query_job.result()
    # # Convert to list of dicts. Required for st.experimental_memo to hash the return value.
    # df = pd.DataFrame([dict(row) for row in rows_raw])
    # return df
    return pd.DataFrame(contributions)


st.set_page_config(layout="wide")

# Print results.
st.title("UN Carbon Offset Dashboard")

contribution_tonnes, contribution_usd = contribution_metrics()
st.metric("Contribution (tonnes)", f"{contribution_tonnes:,.2f}")
st.metric("Contribution (USD)", f"${contribution_usd:,.2f}")

project_id = st.selectbox("Project ID", KNOWN_PROJECT_ID, index=0)

df_history = contribution_history(project_id)

registration_date, project_url, project_name = project_info(project_id)

st.subheader(project_name)

st.markdown(f"Click [here]({project_url}) for more project information")

st.write(
    "**Project Registration Date:**", datetime.strftime(registration_date, "%d %B %Y")
)

st.write(f"**Number of Contributions for Project {project_id}:**", len(df_history))

st.dataframe(
    df_history[
        ["order_id", "contributor", "contribution_date", "contribution", "certificate"]
    ],
    height=500,
)
