# -*- coding: utf-8 -*-

import datetime
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import re
from typing import Any, Dict, List

import scrapy
from dateutil.parser import parse as dateutil_parse
from scrapy import Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import (Compose, Identity, Join, MapCompose,
                                      TakeFirst)
from w3lib.html import remove_tags
from yapic import json

DEBUG = False


def num_page_extractor(num_pages):
    if num_pages:
        return num_pages.split()[0]
    return None


def safe_parse_date(date):
    try:
        date = dateutil_parse(date, fuzzy=True, default=datetime.datetime.min)
        date = date.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        date = None

    return date


def extract_publish_dates(maybe_dates):
    maybe_dates = [s for s in maybe_dates if "published" in s.lower()]
    return [safe_parse_date(date) for date in maybe_dates]


def extract_year(s):
    s = s.lower().strip()
    match = re.match(".*first published.*(\d{4})", s)
    if match:
        return match.group(1)


def extract_ratings(txt):
    """Extract the rating histogram from embedded Javascript code

    The embedded code looks like this:

    |----------------------------------------------------------|
    | renderRatingGraph([6, 3, 2, 2, 1]);                      |
    | if ($('rating_details')) {                               |
    |   $('rating_details').insert({top: $('rating_graph')})   |
    |  }                                                       |
    |----------------------------------------------------------|
    """
    codelines = "".join(txt).split(";")
    rating_code = [line.strip() for line in codelines if "renderRatingGraph" in line]
    if not rating_code:
        return None
    rating_code = rating_code[0]
    rating_array = rating_code[rating_code.index("[") + 1 : rating_code.index("]")]
    return extract_ratings_from_list([int(i) for i in rating_array.split(",")])


def extract_ratings_from_list(ratings: List[int]) -> Dict[int, int]:
    ratings_dict = {5 - i: x for i, x in enumerate(ratings)}
    return ratings_dict


def filter_asin(asin):
    if asin and len(str(asin)) == 10:
        return asin
    return None


def isbn_filter(isbn):
    if isbn and len(str(isbn)) == 10 and isbn.isdigit():
        return isbn


def isbn13_filter(isbn):
    if isbn and len(str(isbn)) == 13 and isbn.isdigit():
        return isbn


def filter_empty(vals):
    return [v.strip() for v in vals if v.strip()]


# added by paul
def remove_more(vals):
    return vals[:-1] + [vals[-1].strip(" ...more")]


def split_by_newline(txt):
    return txt.split("\n")


def visit_path(data: Dict[str, Any], key: str, original_key: str):
    if DEBUG:
        print(f"Processing {key} for {data.keys() if type(data) == dict else data}")

    if not data:
        if key and DEBUG:
            print(f"No data found for key {original_key} in data")
            print(data)
        return None

    # if no key is left, then yield the data at this point
    if not key:
        yield data
        # stop the generator since there is no more key left to parse
        return None

    if "." in key:
        idx = key.index(".")
        subkey, remaining_key = key[:idx], key[idx + 1 :]
    else:
        subkey, remaining_key = key, None

    # handle partial matches on the key
    # this is needed when the key can be dynamic
    if subkey.endswith("*"):
        # remove '*'
        subkey_prefix = subkey[:-1]

        # find all keys which match subkey_prefix
        matching_subkeys = [k for k in data.keys() if k.startswith(subkey_prefix)]

        for sk in matching_subkeys:
            yield from visit_path(data[sk], remaining_key, original_key)

        return None

    # handle arrays
    if subkey.endswith("[]"):
        # remove '[]'
        subkey = subkey[:-2]

        values = data.get(subkey, [])

        for value in values:
            yield from visit_path(value, remaining_key, original_key)

        return None

    # handle multiple comma-separated keys
    # this must be the leaf, because it doesn't make sense to extract more fields
    # from differently keyed values (at least for now)
    if subkey.startswith("[") and subkey.endswith("]"):
        subkeys = subkey[1:-1].split(",")
        value = {}
        for sk in subkeys:
            value[sk] = data.get(sk, None)
        yield value

        return None

    # handle regular keys
    yield from visit_path(data.get(subkey, None), remaining_key, original_key)

    return None


def json_field_extractor_v2(key: str):
    def extract_field(text: str):
        data = json.loads(text)
        return list(visit_path(data, key, key))

    return extract_field


# class BookItem(scrapy.Item):
#     # Scalars
#     url = Field()

#     cover_image = Field(input_processor=MapCompose(str.strip)) # added by paul
#     title = Field(input_processor=MapCompose(str.strip))
#     author = Field(input_processor=MapCompose(str.strip))

#     # description = Field(input_processor=MapCompose(str.strip))
#     description = Field(
#         # Take the last match, remove HTML tags, convert to list of lines, remove empty lines, remove the "edit data" prefix
#         input_processor=Compose(TakeFirst(), remove_tags, split_by_newline, filter_empty, remove_more),
#         output_processor=Join()
#     )
#     #  lambda s: s[1:]

#     num_ratings = Field(input_processor=MapCompose(str.strip, int))
#     num_reviews = Field(input_processor=MapCompose(str.strip, int))
#     avg_rating = Field(input_processor=MapCompose(str.strip, float))
#     num_pages = Field(input_processor=MapCompose(str.strip, num_page_extractor, int))

#     language = Field(input_processor=MapCompose(str.strip))
#     publish_date = Field(input_processor=extract_publish_dates)

#     original_publish_year = Field(input_processor=MapCompose(extract_year, int))

#     isbn = Field(input_processor=MapCompose(str.strip, isbn_filter))
#     isbn13 = Field(input_processor=MapCompose(str.strip, isbn13_filter))
#     asin = Field(input_processor=MapCompose(filter_asin))

#     series = Field()

#     # Lists
#     awards = Field(output_processor=Identity())
#     places = Field(output_processor=Identity())
#     characters = Field(output_processor=Identity())
#     genres = Field(output_processor=Compose(set, list))

#     # Dicts
#     rating_histogram = Field(input_processor=MapCompose(extract_ratings))


class BookItem(scrapy.Item):
    # Scalars
    url = Field()

    # TODO: I don't like this code from havanagrawal, simplify it
    title = Field(
        input_processor=MapCompose(
            json_field_extractor_v2("props.pageProps.apolloState.Book*.title")
        )
    )
    # title_complete = Field(
    #     input_processor=MapCompose(
    #         json_field_extractor_v2("props.pageProps.apolloState.Book*.titleComplete")
    #     )
    # )
    description = Field(
        input_processor=MapCompose(
            json_field_extractor_v2("props.pageProps.apolloState.Book*.description"),
            remove_tags,
        )
    )
    cover_image = Field(
        input_processor=MapCompose(
            json_field_extractor_v2("props.pageProps.apolloState.Book*.imageUrl")
        )
    )
    genres = Field(
        input_processor=MapCompose(
            json_field_extractor_v2(
                "props.pageProps.apolloState.Book*.bookGenres[].genre.name"
            )
        ),
        output_processor=Compose(set, list),
    )
    asin = Field(
        input_processor=MapCompose(
            json_field_extractor_v2("props.pageProps.apolloState.Book*.details.asin")
        )
    )
    isbn = Field(
        input_processor=MapCompose(
            json_field_extractor_v2("props.pageProps.apolloState.Book*.details.isbn")
        )
    )
    isbn13 = Field(
        input_processor=MapCompose(
            json_field_extractor_v2("props.pageProps.apolloState.Book*.details.isbn13")
        )
    )
    # TODO: update model to accept this field
    # publisher = Field(
    #     input_processor=MapCompose(
    #         json_field_extractor_v2(
    #             "props.pageProps.apolloState.Book*.details.publisher"
    #         )
    #     )
    # )
    publish_date = Field(
        input_processor=MapCompose(
            json_field_extractor_v2(
                "props.pageProps.apolloState.Book*.details.publicationTime"
            )
        )
    )
    series = Field(
        input_processor=MapCompose(
            json_field_extractor_v2("props.pageProps.apolloState.Series*.title")
        ),
        output_processor=Compose(set, list),
    )

    # TODO: support multiple authors later
    author = Field(
        input_processor=MapCompose(
            json_field_extractor_v2("props.pageProps.apolloState.Contributor*.name")
        ),
        output_processor=Compose(list, TakeFirst()),
        # output_processor=Compose(set, list, TakeFirst()),
    )

    places = Field(
        input_processor=MapCompose(
            json_field_extractor_v2(
                "props.pageProps.apolloState.Work*.details.places[].name"
            )
        ),
        output_processor=Compose(set, list),
    )
    characters = Field(
        input_processor=MapCompose(
            json_field_extractor_v2(
                "props.pageProps.apolloState.Work*.details.characters[].name"
            )
        ),
        output_processor=Compose(set, list),
    )
    awards = Field(
        input_processor=MapCompose(
            json_field_extractor_v2(
                "props.pageProps.apolloState.Work*.details.awardsWon[].[name,awardedAt,category,hasWon]"
            )
        ),
        output_processor=Identity(),
    )

    num_ratings = Field(
        input_processor=MapCompose(
            json_field_extractor_v2(
                "props.pageProps.apolloState.Work*.stats.ratingsCount"
            )
        )
    )
    num_reviews = Field(
        input_processor=MapCompose(
            json_field_extractor_v2(
                "props.pageProps.apolloState.Work*.stats.textReviewsCount"
            )
        )
    )
    avg_rating = Field(
        input_processor=MapCompose(
            json_field_extractor_v2(
                "props.pageProps.apolloState.Work*.stats.averageRating"
            )
        )
    )
    rating_histogram = Field(
        input_processor=MapCompose(
            json_field_extractor_v2(
                "props.pageProps.apolloState.Work*.stats.ratingsCountDist"
            )
        ),
        output_processor=Compose(MapCompose(extract_ratings_from_list), TakeFirst()),
        # output_processor=extract_ratings_from_list,
    )

    num_pages = Field(
        input_processor=MapCompose(
            json_field_extractor_v2(
                "props.pageProps.apolloState.Book*.details.numPages"
            )
        )
    )
    language = Field(
        input_processor=MapCompose(
            json_field_extractor_v2(
                "props.pageProps.apolloState.Book*.details.language.name"
            )
        )
    )
    format = Field(
        input_processor=MapCompose(
            json_field_extractor_v2(
                "props.pageProps.apolloState.Book*.details.language.format"
            )
        )
    )


class BookLoader(ItemLoader):
    default_output_processor = TakeFirst()


class AuthorItem(scrapy.Item):
    # Scalars
    url = Field()

    name = Field()
    birth_date = Field(input_processor=MapCompose(safe_parse_date))
    death_date = Field(input_processor=MapCompose(safe_parse_date))

    avg_rating = Field(serializer=float)
    num_ratings = Field(serializer=int)
    num_reviews = Field(serializer=int)

    # Lists
    genres = Field(output_processor=Compose(set, list))
    influences = Field(output_processor=Compose(set, list))

    # Blobs
    about = Field(
        # Take the first match, remove HTML tags, convert to list of lines, remove empty lines, remove the "edit data" prefix
        input_processor=Compose(
            TakeFirst(),
            remove_tags,
            split_by_newline,
            filter_empty,
            remove_more,
            lambda s: s[1:],
        ),
        output_processor=Join(),
    )


class AuthorLoader(ItemLoader):
    default_output_processor = TakeFirst()
