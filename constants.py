CONTRIBUTION_HISTORY_BASE_URL = "https://offset.climateneutralnow.org/vchistory"
CONTRIBUTION_HISTORY_URL = "https://offset.climateneutralnow.org/vchistory?ProjectId={project_id}&pageNumber={page}"
CONTRIBUTION_REDIRECT_URL = "https://offset.climateneutralnow.org/changelanguage/1?returnUrl=%2Fvchistory%3FProjectIdString%3D{project_id}%26pageNumber%3D{page}"
PROJECT_URL = "https://offset.climateneutralnow.org/{project_name}-{project_id}-"

PROJECT_INFO_QUERY_URL = (
    "https://cdm.unfccc.int/Projects/storeSearchParameters?Ref={project_id}"
)

ATTESTATION_URL = "https://cdm.unfccc.int/Registry/vc_attest/index.html"
ATTESTATION_2018_URL = "https://cdm.unfccc.int/Registry/vc_attest_old/index.html"
ATTESTATION_ARCHIVE_URL = "https://cdm.unfccc.int/Registry/vc_attest_old/index_archive.html"

CONTRIBUTION_METRIC_XPATHS = (
    '//*[@id="filter-grid-view-div-container"]/div/div[3]/div[2]/div[2]/div[1]/text()',
    '//*[@id="filter-grid-view-div-container"]/div/div[3]/div[2]/div[2]/div[3]/text()',
)
CONTRIBUTION_HISTORY_PAGINATION_XPATH = (
    '//*[@id="filter-grid-view-div-container"]/div/div[5]/ul/li/a'
)
CONTRIBUTION_CARD_XPATH = '//*[@id="filter-grid-view-div-container"]/div/div[4]/div/div'

PROJECT_INFO_REGISTRATION_DATE_XPATH = (
    '//*[@id="projectsTable"]/table/tr[4]/td[1]/text()'
)
PROJECT_INFO_PROJECT_XPATH = '//*[@id="projectsTable"]/table/tr[4]/td[2]/a'

PROJECT_AVAILABILITY_XPATH = '//*[@id="product-details-form"]'
PROJECT_AVAILABILITY_PRICE_SUB_XPATH = 'section/div[2]/div[1]/p/text()'
PROJECT_AVAILABILITY_TONNES_SUB_XPATH = 'section/div[2]/div[1]/table/tbody/tr[4]/td/text()'

ATTESTATION_XPATH = '//*[@id="vc-attest"]/tbody/tr'

ATTESTATION_ID_REGEX = r"\/(?P<year>\d{4})_(?P<suffix>\d+)_(?P<prefix>\w+)\%20"

VC_CERTIFICATE = "{prefix}{suffix}/{year}"

KNOWN_PROJECT_ID = (
    1,
    33,
    86,
    222,
    244,
    258,
    259,
    264,
    267,
    297,
    312,
    328,
    329,
    346,
    363,
    373,
    491,
    557,
    648,
    697,
    773,
    836,
    923,
    935,
    986,
    1254,
    1265,
    1269,
    1326,
    1364,
    1483,
    1514,
    1541,
    1558,
    1642,
    1667,
    1719,
    1787,
    1797,
    1800,
    1836,
    1904,
    1966,
    2138,
    2170,
    2342,
    2470,
    2698,
    2793,
    2936,
    3022,
    3238,
    3248,
    3335,
    3374,
    3493,
    3568,
    3660,
    3815,
    3839,
    3926,
    4052,
    4211,
    4229,
    4317,
    4451,
    4463,
    4489,
    4521,
    4676,
    4744,
    4800,
    4828,
    4985,
    4988,
    4993,
    5016,
    5080,
    5098,
    5161,
    5336,
    5344,
    5401,
    5425,
    5461,
    5486,
    5495,
    5553,
    5887,
    5923,
    5977,
    6121,
    6125,
    6151,
    6275,
    6315,
    6381,
    6465,
    6651,
    6652,
    6702,
    6848,
    6973,
    6987,
    7133,
    7437,
    7461,
    7507,
    7675,
    7980,
    8018,
    8027,
    8269,
    8273,
    8288,
    8374,
    8438,
    8474,
    8495,
    8855,
    8971,
    9111,
    9251,
    9330,
    9347,
    9510,
    9625,
    9626,
    9925,
    9927,
    9933,
    9973,
    10076,
    10122,
    10182,
    10345,
    10360,
)
