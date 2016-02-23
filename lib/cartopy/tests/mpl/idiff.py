#!/usr/bin/env python
"""
Provides "diff-like" comparison of images.

Currently relies on matplotlib for image processing so limited to PNG format.

"""

import os.path
import shutil

import matplotlib.pyplot as plt
import matplotlib.image as mimg
import matplotlib.widgets as mwidget

from cartopy.tests.mpl import ImageTesting


def diff_viewer(expected_fname, result_fname, diff_fname):
    plt.figure(figsize=(16, 16))
    plt.suptitle(os.path.basename(expected_fname))
    ax = plt.subplot(221)
    ax.imshow(mimg.imread(expected_fname))
    ax = plt.subplot(222, sharex=ax, sharey=ax)
    ax.imshow(mimg.imread(result_fname))
    ax = plt.subplot(223, sharex=ax, sharey=ax)
    ax.imshow(mimg.imread(diff_fname))

    def accept(event):
        # removes the expected result, and move the most recent result in
        print 'ACCEPTED NEW FILE: %s' % (os.path.basename(expected_fname), )
        os.remove(expected_fname)
        shutil.copy2(result_fname, expected_fname)
        os.remove(diff_fname)
        plt.close()

    def reject(event):
        print 'REJECTED: %s' % (os.path.basename(expected_fname), )
        plt.close()

    ax_accept = plt.axes([0.7, 0.05, 0.1, 0.075])
    ax_reject = plt.axes([0.81, 0.05, 0.1, 0.075])
    bnext = mwidget.Button(ax_accept, 'Accept change')
    bnext.on_clicked(accept)
    bprev = mwidget.Button(ax_reject, 'Reject')
    bprev.on_clicked(reject)

    plt.show()


def step_over_diffs():
    image_dir = os.path.join(ImageTesting.root_image_results, 'baseline_images', 'mpl')
    diff_dir = os.path.join(ImageTesting.image_output_directory)

    import glob

    for expected_fname in sorted(glob.glob(os.path.join(image_dir, '*', '*.png'))):
        expected_rel = os.path.relpath(expected_fname, os.path.dirname(os.path.dirname(expected_fname)))
        result_path = os.path.join(diff_dir, os.path.dirname(expected_rel),
                                   'result-' + os.path.basename(expected_rel))
        diff_path = result_path[:-4] + '-failed-diff.png'
        # if the test failed, there will be a diff file
        if os.path.exists(diff_path):
            expected_path = expected_fname
            diff_viewer(expected_path, result_path, diff_path)


if __name__ == '__main__':
    step_over_diffs()
