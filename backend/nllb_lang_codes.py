"""
Complete NLLB Language Code Mappings
Maps ISO 639-1 (2-letter) and ISO 639-3 (3-letter) codes to NLLB language codes.
"""

# Comprehensive mapping from ISO codes to NLLB codes
# Format: "iso_code": "nllb_code"
LANG_CODE_MAP = {
    # Major World Languages
    "en": "eng_Latn", "eng": "eng_Latn",  # English
    "es": "spa_Latn", "spa": "spa_Latn",  # Spanish
    "fr": "fra_Latn", "fra": "fra_Latn",  # French
    "de": "deu_Latn", "deu": "deu_Latn",  # German
    "it": "ita_Latn", "ita": "ita_Latn",  # Italian
    "pt": "por_Latn", "por": "por_Latn",  # Portuguese
    "ru": "rus_Cyrl", "rus": "rus_Cyrl",  # Russian
    "zh": "zho_Hans", "zho": "zho_Hans",  # Chinese (Simplified)
    "zh-cn": "zho_Hans",  # Chinese Simplified (langdetect specific)
    "zh-tw": "zho_Hant",  # Chinese Traditional (langdetect specific)
    "ar": "arb_Arab", "arb": "arb_Arab",  # Arabic (Modern Standard)
    "ja": "jpn_Jpan", "jpn": "jpn_Jpan",  # Japanese
    "ko": "kor_Hang", "kor": "kor_Hang",  # Korean
    "hi": "hin_Deva", "hin": "hin_Deva",  # Hindi

    # European Languages
    "nl": "nld_Latn", "nld": "nld_Latn",  # Dutch
    "pl": "pol_Latn", "pol": "pol_Latn",  # Polish
    "tr": "tur_Latn", "tur": "tur_Latn",  # Turkish
    "sv": "swe_Latn", "swe": "swe_Latn",  # Swedish
    "da": "dan_Latn", "dan": "dan_Latn",  # Danish
    "no": "nob_Latn", "nob": "nob_Latn",  # Norwegian (Bokmål)
    "nb": "nob_Latn",  # Norwegian Bokmål
    "nn": "nno_Latn", "nno": "nno_Latn",  # Norwegian Nynorsk
    "fi": "fin_Latn", "fin": "fin_Latn",  # Finnish
    "cs": "ces_Latn", "ces": "ces_Latn",  # Czech
    "ro": "ron_Latn", "ron": "ron_Latn",  # Romanian
    "el": "ell_Grek", "ell": "ell_Grek",  # Greek
    "he": "heb_Hebr", "heb": "heb_Hebr",  # Hebrew
    "hu": "hun_Latn", "hun": "hun_Latn",  # Hungarian
    "uk": "ukr_Cyrl", "ukr": "ukr_Cyrl",  # Ukrainian
    "bg": "bul_Cyrl", "bul": "bul_Cyrl",  # Bulgarian
    "ca": "cat_Latn", "cat": "cat_Latn",  # Catalan
    "hr": "hrv_Latn", "hrv": "hrv_Latn",  # Croatian
    "sr": "srp_Cyrl", "srp": "srp_Cyrl",  # Serbian
    "sk": "slk_Latn", "slk": "slk_Latn",  # Slovak
    "sl": "slv_Latn", "slv": "slv_Latn",  # Slovenian
    "lt": "lit_Latn", "lit": "lit_Latn",  # Lithuanian
    "lv": "lvs_Latn", "lvs": "lvs_Latn",  # Latvian
    "et": "est_Latn", "est": "est_Latn",  # Estonian
    "sq": "als_Latn", "als": "als_Latn",  # Albanian
    "bs": "bos_Latn", "bos": "bos_Latn",  # Bosnian
    "mk": "mkd_Cyrl", "mkd": "mkd_Cyrl",  # Macedonian
    "be": "bel_Cyrl", "bel": "bel_Cyrl",  # Belarusian
    "is": "isl_Latn", "isl": "isl_Latn",  # Icelandic
    "ga": "gle_Latn", "gle": "gle_Latn",  # Irish
    "cy": "cym_Latn", "cym": "cym_Latn",  # Welsh
    "mt": "mlt_Latn", "mlt": "mlt_Latn",  # Maltese
    "gl": "glg_Latn", "glg": "glg_Latn",  # Galician
    "eu": "eus_Latn", "eus": "eus_Latn",  # Basque

    # Middle Eastern Languages
    "fa": "pes_Arab", "pes": "pes_Arab",  # Persian/Farsi
    "ur": "urd_Arab", "urd": "urd_Arab",  # Urdu
    "az": "azj_Latn", "azj": "azj_Latn",  # Azerbaijani (Latin)
    "ku": "kmr_Latn", "kmr": "kmr_Latn",  # Kurdish (Kurmanji)
    "hy": "hye_Armn", "hye": "hye_Armn",  # Armenian
    "ka": "kat_Geor", "kat": "kat_Geor",  # Georgian
    "yi": "ydd_Hebr", "ydd": "ydd_Hebr",  # Yiddish
    "ps": "pbt_Arab", "pbt": "pbt_Arab",  # Pashto
    "sd": "snd_Arab", "snd": "snd_Arab",  # Sindhi

    # South Asian Languages
    "bn": "ben_Beng", "ben": "ben_Beng",  # Bengali
    "ta": "tam_Taml", "tam": "tam_Taml",  # Tamil
    "te": "tel_Telu", "tel": "tel_Telu",  # Telugu
    "mr": "mar_Deva", "mar": "mar_Deva",  # Marathi
    "gu": "guj_Gujr", "guj": "guj_Gujr",  # Gujarati
    "kn": "kan_Knda", "kan": "kan_Knda",  # Kannada
    "ml": "mal_Mlym", "mal": "mal_Mlym",  # Malayalam
    "pa": "pan_Guru", "pan": "pan_Guru",  # Punjabi
    "or": "ory_Orya", "ory": "ory_Orya",  # Odia
    "as": "asm_Beng", "asm": "asm_Beng",  # Assamese
    "ne": "npi_Deva", "npi": "npi_Deva",  # Nepali
    "si": "sin_Sinh", "sin": "sin_Sinh",  # Sinhala

    # Southeast Asian Languages
    "th": "tha_Thai", "tha": "tha_Thai",  # Thai
    "vi": "vie_Latn", "vie": "vie_Latn",  # Vietnamese
    "id": "ind_Latn", "ind": "ind_Latn",  # Indonesian
    "ms": "zsm_Latn", "zsm": "zsm_Latn",  # Malay
    "tl": "tgl_Latn", "tgl": "tgl_Latn",  # Tagalog
    "jv": "jav_Latn", "jav": "jav_Latn",  # Javanese
    "su": "sun_Latn", "sun": "sun_Latn",  # Sundanese
    "my": "mya_Mymr", "mya": "mya_Mymr",  # Burmese
    "km": "khm_Khmr", "khm": "khm_Khmr",  # Khmer
    "lo": "lao_Laoo", "lao": "lao_Laoo",  # Lao
    "ceb": "ceb_Latn",  # Cebuano
    "ilo": "ilo_Latn",  # Ilocano

    # Central Asian Languages
    "kk": "kaz_Cyrl", "kaz": "kaz_Cyrl",  # Kazakh
    "uz": "uzn_Latn", "uzn": "uzn_Latn",  # Uzbek
    "ky": "kir_Cyrl", "kir": "kir_Cyrl",  # Kyrgyz
    "tg": "tgk_Cyrl", "tgk": "tgk_Cyrl",  # Tajik
    "tk": "tuk_Latn", "tuk": "tuk_Latn",  # Turkmen
    "mn": "khk_Cyrl", "khk": "khk_Cyrl",  # Mongolian

    # African Languages
    "sw": "swh_Latn", "swh": "swh_Latn",  # Swahili
    "af": "afr_Latn", "afr": "afr_Latn",  # Afrikaans
    "am": "amh_Ethi", "amh": "amh_Ethi",  # Amharic
    "ha": "hau_Latn", "hau": "hau_Latn",  # Hausa
    "ig": "ibo_Latn", "ibo": "ibo_Latn",  # Igbo
    "yo": "yor_Latn", "yor": "yor_Latn",  # Yoruba
    "zu": "zul_Latn", "zul": "zul_Latn",  # Zulu
    "xh": "xho_Latn", "xho": "xho_Latn",  # Xhosa
    "sn": "sna_Latn", "sna": "sna_Latn",  # Shona
    "so": "som_Latn", "som": "som_Latn",  # Somali
    "rw": "kin_Latn", "kin": "kin_Latn",  # Kinyarwanda
    "ny": "nya_Latn", "nya": "nya_Latn",  # Nyanja/Chichewa
    "mg": "plt_Latn", "plt": "plt_Latn",  # Malagasy
    "ti": "tir_Ethi", "tir": "tir_Ethi",  # Tigrinya
    "om": "gaz_Latn", "gaz": "gaz_Latn",  # Oromo
    "lg": "lug_Latn", "lug": "lug_Latn",  # Luganda
    "wo": "wol_Latn", "wol": "wol_Latn",  # Wolof
    "ln": "lin_Latn", "lin": "lin_Latn",  # Lingala
    "ts": "tso_Latn", "tso": "tso_Latn",  # Tsonga
    "tn": "tsn_Latn", "tsn": "tsn_Latn",  # Tswana
    "st": "sot_Latn", "sot": "sot_Latn",  # Southern Sotho
    "ss": "ssw_Latn", "ssw": "ssw_Latn",  # Swati
    "ve": "ven_Latn", "ven": "ven_Latn",  # Venda
    "nso": "nso_Latn",  # Northern Sotho
    "lua": "lua_Latn",  # Luba-Kasai
    "luo": "luo_Latn",  # Luo
    "bam": "bam_Latn",  # Bambara
    "ful": "fuv_Latn",  # Fulah
    "ewe": "ewe_Latn",  # Ewe
    "twi": "twi_Latn",  # Twi
    "fon": "fon_Latn",  # Fon
    "mos": "mos_Latn",  # Mossi
    "dyu": "dyu_Latn",  # Dyula
    "kon": "kon_Latn",  # Kikongo
    "tum": "tum_Latn",  # Tumbuka
    "run": "run_Latn",  # Rundi

    # Other Languages
    "eo": "epo_Latn", "epo": "epo_Latn",  # Esperanto
    "la": "lat_Latn", "lat": "lat_Latn",  # Latin
    "haw": "haw_Latn",  # Hawaiian
    "mi": "mri_Latn", "mri": "mri_Latn",  # Maori
    "sm": "smo_Latn", "smo": "smo_Latn",  # Samoan
    "to": "ton_Latn", "ton": "ton_Latn",  # Tongan
}

# Additional NLLB codes not covered by langdetect
# These can be used if you know the exact NLLB code
ADDITIONAL_NLLB_CODES = [
    "ace_Arab", "ace_Latn", "acm_Arab", "acq_Arab", "aeb_Arab", "afr_Latn",
    "ajp_Arab", "aka_Latn", "als_Latn", "amh_Ethi", "apc_Arab", "arb_Arab",
    "arb_Latn", "ars_Arab", "ary_Arab", "arz_Arab", "asm_Beng", "ast_Latn",
    "awa_Deva", "ayr_Latn", "azb_Arab", "azj_Latn", "bak_Cyrl", "bam_Latn",
    "ban_Latn", "bel_Cyrl", "bem_Latn", "ben_Beng", "bho_Deva", "bjn_Arab",
    "bjn_Latn", "bod_Tibt", "bos_Latn", "bug_Latn", "bul_Cyrl", "cat_Latn",
    "ceb_Latn", "ces_Latn", "cjk_Latn", "ckb_Arab", "crh_Latn", "cym_Latn",
    "dan_Latn", "deu_Latn", "dik_Latn", "dyu_Latn", "dzo_Tibt", "ell_Grek",
    "eng_Latn", "epo_Latn", "est_Latn", "eus_Latn", "ewe_Latn", "fao_Latn",
    "fij_Latn", "fin_Latn", "fon_Latn", "fra_Latn", "fur_Latn", "fuv_Latn",
    "gaz_Latn", "gla_Latn", "gle_Latn", "glg_Latn", "grn_Latn", "guj_Gujr",
    "hat_Latn", "hau_Latn", "heb_Hebr", "hin_Deva", "hne_Deva", "hrv_Latn",
    "hun_Latn", "hye_Armn", "ibo_Latn", "ilo_Latn", "ind_Latn", "isl_Latn",
    "ita_Latn", "jav_Latn", "jpn_Jpan", "kab_Latn", "kac_Latn", "kam_Latn",
    "kan_Knda", "kas_Arab", "kas_Deva", "kat_Geor", "kaz_Cyrl", "kbp_Latn",
    "kea_Latn", "khk_Cyrl", "khm_Khmr", "kik_Latn", "kin_Latn", "kir_Cyrl",
    "kmb_Latn", "kmr_Latn", "knc_Arab", "knc_Latn", "kon_Latn", "kor_Hang",
    "lao_Laoo", "lat_Latn", "lij_Latn", "lim_Latn", "lin_Latn", "lit_Latn",
    "lmo_Latn", "ltg_Latn", "ltz_Latn", "lua_Latn", "lug_Latn", "luo_Latn",
    "lus_Latn", "lvs_Latn", "mag_Deva", "mai_Deva", "mal_Mlym", "mar_Deva",
    "min_Arab", "min_Latn", "mkd_Cyrl", "mlt_Latn", "mni_Beng", "mos_Latn",
    "mri_Latn", "mya_Mymr", "nld_Latn", "nno_Latn", "nob_Latn", "npi_Deva",
    "nso_Latn", "nus_Latn", "nya_Latn", "oci_Latn", "ory_Orya", "pag_Latn",
    "pan_Guru", "pap_Latn", "pbt_Arab", "pes_Arab", "plt_Latn", "pol_Latn",
    "por_Latn", "prs_Arab", "quy_Latn", "ron_Latn", "run_Latn", "rus_Cyrl",
    "sag_Latn", "san_Deva", "sat_Olck", "scn_Latn", "shn_Mymr", "sin_Sinh",
    "slk_Latn", "slv_Latn", "smo_Latn", "sna_Latn", "snd_Arab", "som_Latn",
    "sot_Latn", "spa_Latn", "srd_Latn", "srp_Cyrl", "ssw_Latn", "sun_Latn",
    "swe_Latn", "swh_Latn", "szl_Latn", "tam_Latn", "tam_Taml", "tat_Cyrl",
    "tel_Telu", "tgk_Cyrl", "tgl_Latn", "tha_Thai", "tir_Ethi", "taq_Latn",
    "taq_Tfng", "ton_Latn", "tpi_Latn", "tsn_Latn", "tso_Latn", "tuk_Latn",
    "tum_Latn", "tur_Latn", "twi_Latn", "tzm_Tfng", "uig_Arab", "ukr_Cyrl",
    "umb_Latn", "urd_Arab", "uzn_Latn", "vec_Latn", "vie_Latn", "war_Latn",
    "wol_Latn", "xho_Latn", "ydd_Hebr", "yor_Latn", "yue_Hant", "zho_Hans",
    "zho_Hant", "zsm_Latn", "zul_Latn"
]

def get_nllb_code(iso_code):
    """
    Get NLLB language code from ISO 639-1 or ISO 639-3 code.
    Returns None if not found.
    """
    if not iso_code:
        return None

    # Direct lookup
    nllb_code = LANG_CODE_MAP.get(iso_code.lower())
    if nllb_code:
        return nllb_code

    # If it's already an NLLB code format (xxx_Xxxx), validate and return
    if "_" in iso_code:
        if iso_code in ADDITIONAL_NLLB_CODES:
            return iso_code
        # Check if it's a valid format
        parts = iso_code.split("_")
        if len(parts) == 2 and len(parts[0]) == 3 and len(parts[1]) == 4:
            return iso_code  # Assume it's valid NLLB code

    return None

def get_all_supported_languages():
    """Get list of all supported language codes."""
    return list(set(LANG_CODE_MAP.values())) + ADDITIONAL_NLLB_CODES
