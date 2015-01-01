""" Pull the raw csv data from the web. """

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import string
import subprocess
import urllib2


OUTPUT_FILE = "special_chars_removed_loan_stats.csv"


def get_urls():
    """ Return urls to download. """
    for val in string.ascii_lowercase[:3]:
        yield "https://resources.lendingclub.com/LoanStats3" + val + "_securev1.csv.zip"


def rm_file(file_name):
    """ Remove a file. """
    subprocess.call(['rm', '-f', file_name])


def download_reports():
    """ Download all the data to files. """
    reports = []
    for url in get_urls():
        file_name = url.split('/')[-1]
        url_handle = urllib2.urlopen(url)
        content = url_handle.read()

        with open(file_name, 'w') as f:
            f.write(content)
        reports.append(file_name)

    return reports


def unzip_reports(reports):
    """ Unzip the files. """
    new_reports = []
    for report in reports:
        subprocess.call(['unzip', report])
        rm_file(report)
        # remove the ".zip"
        new_report = report[:-4]
        new_reports.append(new_report)

    return new_reports


def cat_to_single_file(reports):
    """ Concatenate the files into one. """
    with open(OUTPUT_FILE, 'w') as f:
        subprocess.Popen(['cat'] + reports, stdout=f).wait()

    for report in reports:
        rm_file(report)


def fetchDataAndReturnFilePath():
    reports = download_reports()
    reports = unzip_reports(reports)
    cat_to_single_file(reports)
    return OUTPUT_FILE


if __name__ == '__main__':
    main()
