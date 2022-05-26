from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Tuple
import re

import pandas as pd
import requests
import streamlit as st
from lxml import html, etree

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
        last_page = 1  # so that range(2, 2) will yield nothing
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
            CONTRIBUTION_HISTORY_URL.format(project_id=project_id, page=i)
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


def get_xpath_text(tree: etree, xpath: str) -> str:

    return tree.xpath(xpath)[0].text_content()


def get_xpath_attrib(tree: etree, xpath: str, attrib: str = "text") -> str:

    if attrib == "text":
        return get_xpath_text(tree, xpath)

    return tree.xpath(xpath)[0].get(attrib)


def parse_attestation(tree: etree) -> Dict:

    return {
        "project_id": int(get_xpath_text(tree, "td[1]/a")),
        "project_url": get_xpath_attrib(tree, "td[1]/a", "href"),
        "project_name": get_xpath_text(tree, "td[2]"),
        "project_type": get_xpath_text(tree, "td[3]"),
        "host_country": get_xpath_text(tree, "td[4]"),
        "quantity": float(get_xpath_text(tree, "td[5]").replace(",", "")),
        "unit": get_xpath_text(tree, "td[6]"),
        "reason": get_xpath_text(tree, "td[7]"),
        "contribution_date": datetime.strptime(
            get_xpath_text(tree, "td[8]/span[2]"), "%d/%m/%Y"
        ),
        "certificate_id": VC_CERTIFICATE.format(
            **next(
                re.finditer(ATTESTATION_ID_REGEX, get_xpath_text(tree, "td[8]/span[1]"))
            )
        ),
        "certificate_url": get_xpath_attrib(tree, "td[9]/a", "href"),
    }


def parse_attestation_2018(tree: etree) -> Dict:

    return {
        "project_id": int(get_xpath_text(tree, "td[1]/a")),
        "project_url": get_xpath_attrib(tree, "td[1]/a", "href"),
        "project_name": get_xpath_text(tree, "td[2]"),
        "project_type": get_xpath_text(tree, "td[3]"),
        "host_country": get_xpath_text(tree, "td[4]"),
        "quantity": float(get_xpath_text(tree, "td[5]").replace(",", "")),
        "unit": get_xpath_text(tree, "td[6]"),
        "reason": get_xpath_text(tree, "td[7]"),
        "contribution_date": datetime.strptime(
            get_xpath_text(tree, "td[8]"), "%d/%m/%Y"
        ),
        "certificate_id": VC_CERTIFICATE.format(
            **next(
                re.finditer(
                    ATTESTATION_ID_REGEX, get_xpath_attrib(tree, "td[9]/a", "href")
                )
            )
        ),
        "certificate_url": get_xpath_attrib(tree, "td[9]/a", "href"),
    }


def attestation_history() -> pd.DataFrame:

    attestation = []

    results = requests.get(ATTESTATION_ARCHIVE_URL).text
    tree = html.fromstring(results)
    attestation.extend([parse_attestation(r) for r in tree.xpath(ATTESTATION_XPATH)])

    results = requests.get(ATTESTATION_2018_URL).text
    tree = html.fromstring(results)
    attestation.extend([parse_attestation(r) for r in tree.xpath(ATTESTATION_XPATH)])

    results = requests.get(ATTESTATION_URL).text
    tree = html.fromstring(results)
    attestation.extend([parse_attestation(r) for r in tree.xpath(ATTESTATION_XPATH)])

    attestation = pd.DataFrame.from_dict(attestation)
    attestation = attestation.sort_values(
        "contribution_date", ascending=False
    ).reset_index(drop=True)

    return attestation


def project_availability(project_url: str) -> Tuple[str, str]:

    tree = html.fromstring(requests.get(project_url).text)

    availability = tree.xpath(PROJECT_AVAILABILITY_XPATH)

    if len(availability) == 0:
        return "N/A", "N/A"
    elif availability[0].text_content() == "":
        return "N/A", "N/A"

    return (
        availability[0].xpath(PROJECT_AVAILABILITY_PRICE_SUB_XPATH)[0],
        availability[0].xpath(PROJECT_AVAILABILITY_TONNES_SUB_XPATH)[0],
    )


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

project_cop_url = PROJECT_URL.format(
    project_name="-".join(
        re.sub(
            r"\W+",
            " ",
            project_name,
        ).split(" ")
    )
    .lower()
    .rstrip("-"),
    project_id=project_id,
)

unit_price, tonnes_available = project_availability(project_cop_url)

st.markdown(
    f"Click [here]({project_cop_url}) to get to Carbon Offset Platform marketplace for this project"
)
st.markdown(f"Click [here]({project_url}) for more project information")

st.write(
    "**Project Registration Date:**", datetime.strftime(registration_date, "%d %B %Y")
)
st.write("**Unit Price:**", unit_price)
st.write("**Availability:**", tonnes_available)

st.write(f"**Number of Contributions for Project {project_id}:**", len(df_history))

st.dataframe(
    df_history[
        ["order_id", "contributor", "contribution_date", "contribution", "certificate"]
    ],
    height=500,
)
