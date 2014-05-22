import os
import io
from docutils.parsers.rst import Directive, directives

from IPython.nbconvert import RSTExporter
from IPython.nbformat import current as nbformat


class Notebook(Directive):
    has_content = False
    required_arguments = 1

    def construct_notebook(self, lines):
        return nbformat.reads_json(lines)

    def create_nbconvert_exporter(self):
        return RSTExporter()

    def convert_to_rst(self, notebook, resources):
        """Return a list of strings representing the rst of the given notebook."""
        exporter = self.create_nbconvert_exporter()

        rst, resources = exporter.from_notebook_node(notebook, resources)
        rst = rst.split('\n')

        # Convert linked resources (such as images) into actual files in the
        # source directory.
        for name, data in resources.get('outputs', {}).items():
            if name.startswith('/'):
                name = self.source_directory + name
            if not os.path.exists(os.path.dirname(name)):
                os.makedirs(os.path.dirname(name))
            with io.open(name, 'wb') as f:
                f.write(data)

        return rst

    def normalized_rel_name(self):
        """
        Normalize the name of the notebook, removing the extension and
        by replacing any relative parent directories above the top level source
        with "parent_dir".

        """
        if len(self.arguments) != 1:
            raise ValueError('Only one argument allowed.')

        document = self.state.document
        env = document.settings.env
        rel_filename, _ = env.relfn2path(self.arguments[0])

        rel_fname_segments = os.path.split(os.path.normpath(rel_filename))

        # Remove any ".." from the path, replacing leading ones with "parent_dir"
        rel_name = os.path.join(*(path_seg if path_seg != '..' else 'parent_dir'
                                  for path_seg in rel_fname_segments))
        # Replace any parent paths (i.e. "..") with "parent_dir".
        name, _ = os.path.splitext(rel_name)
        return name

    @property
    def resources_dir(self):
        """
        The resources directory for this notebook. This is *always* within
        the `notebook_resources` folder inside the top level source of
        the Sphinx project. 

        """
        return os.path.join('notebook_resources', self.normalized_rel_name())

    def run(self):
        document = self.state.document
        env = document.settings.env

        _, filename = env.relfn2path(self.arguments[0])

        with open(filename, 'r') as fh:
            raw_notebook = '\n'.join(fh)

        notebook = self.construct_notebook(raw_notebook)

        #: The top level directory of the rst source. 
        self.source_directory = env.srcdir

        name = os.path.splitext(os.path.basename(filename))[0]
        # Insert a leading slash before the resources_dir to tell sphinx
        # to use this as an path *relative* to the source directory.
        resources = dict(unique_key=name,
                         output_files_dir='/' + self.resources_dir)

        lines = self.convert_to_rst(notebook, resources)
        # Insert a reference at the top of the notebook
        norm_name = self.normalized_rel_name()
        lines = ['.. _notebook_{}::'.format(norm_name.replace(os.path.sep, '__')),
                 ''] + lines

        # The filename of the source relative to the top level of the top level
        # of the Sphinx project's source directory.
        rst_source_suffix = os.path.join(self.resources_dir, 'source.rst.txt')
        rst_source_fname = os.path.join(self.source_directory,
                                        rst_source_suffix)

        write_source = True
        if os.path.exists(rst_source_fname):
            with open(rst_source_fname, 'r') as fh:
                current_lines = fh.readlines()
            if current_lines != lines:
                write_source = False

        if write_source:
            with open(rst_source_fname, 'w') as fh:
                fh.writelines(lines)

        # Insert the reST lines into the source to be rendered.
        self.state_machine.insert_input(lines, rst_source_suffix)
        return []


directives.register_directive('notebook', Notebook)


try:
    from nose.tools import assert_equal
    import mock
except ImportError:
    pass


class TestNotebookDirective(object):
    def nb_directive(self, arguments):
        from sphinx.environment import BuildEnvironment

        # Define the necessary components of the directive's environment.
        state = mock.Mock()
        config = mock.Mock(nitpick_ignore=[False],
                           source_suffix='.rst')
        env = BuildEnvironment('src_dir', 'doctree_dir',
                               config=config)
        env.temp_data = {'docname': 'docname'}
        state.document.settings.env = env

        return mock.Mock(spec=Notebook, arguments=arguments, state=state)

    def assert_norm_name(self, fname, expected):
        # Check that the given relative fname gets converted to something
        # which could be used in the resources directory, for example.
        nb_directive = self.nb_directive([fname])
        actual = Notebook.normalized_rel_name(nb_directive)
        assert_equal(expected, actual)

    def test_path_normailisation(self):
        self.assert_norm_name('simple.ipynb', 'simple')
        self.assert_norm_name('../nb.ipynb', 'parent_dir/nb')
        self.assert_norm_name('/../nb.ipynb', 'parent_dir/nb')
        self.assert_norm_name('another/../simple.ipynb', 'simple')
        self.assert_norm_name('another/simple.ipynb', 'another/simple')
        self.assert_norm_name('/another/simple.ipynb', 'another/simple')


if __name__ == '__main__':
    import nose
    nose.runmodule(argv=['-s', '--with-doctest'], exit=False)
