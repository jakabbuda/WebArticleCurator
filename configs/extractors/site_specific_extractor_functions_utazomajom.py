#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

from os.path import abspath, dirname, join as os_path_join

from bs4 import BeautifulSoup

from webarticlecurator import WarcCachingDownloader, Logger


# BEGIN SITE SPECIFIC extract_next_page_url FUNCTIONS ##################################################################


def extract_next_page_url_utazomajom(archive_page_raw_html):
    """extracts and returns next page URL from an HTML code if there is one...
        Specific for https://utazomajom.hu/kategoria/elmenybeszamolok
        :returns string of url if there is one, None otherwise"""
    ret = None
    soup = BeautifulSoup(archive_page_raw_html, 'lxml')
    next_page = soup.find('a', class_='paginator-next')
    if next_page is not None and next_page.has_attr('href'):
        ret = next_page.attrs['href']
    return ret


def extract_next_page_url_test(filename, test_logger):
    """Quick test for extracting "next page" URLs when needed"""
    # This function is intended to be used from this file only as the import of WarcCachingDownloader is local to main()
    w = WarcCachingDownloader(filename, None, test_logger, just_cache=True, download_params={'stay_offline': True})

    # Some of these are intentionally yields None
    test_logger.log('INFO', 'Testing utazomajom')
    text = w.download_url('https://utazomajom.hu/kategoria/elmenybeszamolok/?q=%2Fkategoria%2Felmenybeszamolok%2F')
    assert extract_next_page_url_utazomajom(text) == \
           'https://utazomajom.hu/kategoria/elmenybeszamolok/page/2/?q=%2Fkategoria%2Felmenybeszamolok%2F'
    text = w.download_url(
        'https://utazomajom.hu/kategoria/elmenybeszamolok/page/5/?q=%2Fkategoria%2Felmenybeszamolok%2F')
    assert extract_next_page_url_utazomajom(text) is None
    test_logger.log('INFO', 'Test OK!')

# END SITE SPECIFIC extract_next_page_url FUNCTIONS ####################################################################

# BEGIN SITE SPECIFIC extract_article_urls_from_page FUNCTIONS #########################################################


def safe_extract_hrefs_from_a_tags(main_container):
    """
    Helper function to extract href from a tags
    :param main_container: An iterator over Tag()-s
    :return: Generator over the extracted links
    """
    for a_tag in main_container:
        a_tag_a = a_tag.find('a')
        if a_tag_a is not None and 'href' in a_tag_a.attrs:
            yield a_tag_a['href']


def extract_article_urls_from_page_utazomajom(archive_page_raw_html):
    """extracts and returns as a list the URLs belonging to articles from an HTML code
    :param archive_page_raw_html: archive page containing list of articles with their URLs
    :return: list that contains URLs"""
    soup = BeautifulSoup(archive_page_raw_html, 'lxml')
    main_container = soup.find_all('h1', class_='article-title')
    urls = {link for link in safe_extract_hrefs_from_a_tags(main_container)}
    return urls


def extract_article_urls_from_page_test(filename, test_logger):
    """Quick test for extracting URLs form an archive page"""
    # This function is intended to be used from this file only as the import of WarcCachingDownloader is local to main()
    w = WarcCachingDownloader(filename, None, test_logger, just_cache=True, download_params={'stay_offline': True})

    test_logger.log('INFO', 'Testing utazomajom')
    text = w.download_url('https://utazomajom.hu/kategoria/elmenybeszamolok/?q=%2Fkategoria%2Felmenybeszamolok%2F')
    extracted = extract_article_urls_from_page_utazomajom(text)
    expected = {'https://utazomajom.hu/egy-ejszakam-az-orosz-vadonban/',
                'https://utazomajom.hu/elmenybeszamolo-egy-varos-a-szomszedban-utazas-kijevbe/',
                'https://utazomajom.hu/legkulonlegesebb-hotelek-ahol-megszalltunk/',
                'https://utazomajom.hu/az-elso-elmenyunk-lakoautoval-4-orszag-5-nap-alatt/',
                'https://utazomajom.hu/utazas-autostoppal/',
                'https://utazomajom.hu/7-ok-hogy-miert-jo-kutyaval-utazni-europaban/',
                'https://utazomajom.hu/olvasoi-elmenybeszamolo-bakurol/',
                'https://utazomajom.hu/elmenybeszamolo-utazas-a-meses-baszkfoldre/',
                'https://utazomajom.hu/elmenybeszamolo-hajoval-a-vilag-korul/',
                'https://utazomajom.hu/francia-polinezia-tahiti-legszebb-latnivaloi/',
                'https://utazomajom.hu/hogyan-eljunk-egy-csodaszigeten-kambodzsaban-egy-honapig-ketten-osszesen-26'
                '-000-forintbol/',
                'https://utazomajom.hu/osztrak-alpesi-paradicsom-ingyenes-extrakkal-letezik/'}

    assert (extracted, len(extracted)) == (expected, 12)

    text = w.download_url('https://utazomajom.hu/kategoria/elmenybeszamolok/page/5/?q=%2Fkategoria%2Felmenybeszamolok'
                          '%2F')
    extracted = extract_article_urls_from_page_utazomajom(text)
    expected = {'https://utazomajom.hu/fulop-szigetek-elmenybeszamolo-bohol/',
                'https://utazomajom.hu/elindulni-12-szer-olvasonk-irta-2-resz/',
                'https://utazomajom.hu/fulop-szigetek-elmenybeszamolo-boracay/',
                'https://utazomajom.hu/hawaii-oahu/',
                'https://utazomajom.hu/szeszelyes-idojaras-es-a-vulkanok-big-island-2-resz/',
                'https://utazomajom.hu/elmenybeszamolo-kinai-nepkoztarsasag/',
                'https://utazomajom.hu/a-kulonleges-japan-elmenybeszamolo/',
                'https://utazomajom.hu/elindulni-12-szer-olvasonk-irta/'}

    assert (extracted, len(extracted)) == (expected, 8)

    test_logger.log('INFO', 'Test OK!')

# END SITE SPECIFIC next_page_of_article FUNCTIONS #####################################################################


def main_test():
    main_logger = Logger()

    # Relateive path from this directory to the files in the project's test directory
    choices = {'nextpage': os_path_join(dirname(abspath(__file__)), '../../tests/next_page_url_utazomajom.warc.gz'),
               'article_nextpage': os_path_join(dirname(abspath(__file__)), '../../tests/next_page_of_article.warc.gz'),
               'archive': os_path_join(dirname(abspath(__file__)),
                                       '../../tests/extract_article_urls_from_page_utazomajom.warc.gz')
               }

    # Use the main module to modify the warc files!
    extract_next_page_url_test(choices['nextpage'], main_logger)
    extract_article_urls_from_page_test(choices['archive'], main_logger)
    # next_page_of_article_test(choices['article_nextpage'], main_logger)


if __name__ == '__main__':
    main_test()
