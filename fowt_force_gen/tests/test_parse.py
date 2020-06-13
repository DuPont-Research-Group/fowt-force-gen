from fowt_force_gen import parse
import numpy as np
import os
import time


class TestDataParse:
    def test_data_parse_1(self):
        # make distributions of list data
        list_data = [5.5, 10.3, 15.67, 20.3, 25.1, 30.5, 35.8]
        stats = parse.make_distributions(list_data)
        compare_stats = np.array([20.453, 10.054])
        assert (stats == compare_stats).all()
    def test_data_parse_2(self):
        # make distributions of np.ndarray data
        array_data = np.array([[52560., 32550., 13520., 10030., 11160., 500.],
                               [52157., 32652., 13126., 10251., 11164., 500.],
                               [54321., 35236., 13633., 10275., 11166., 500.],
                               [56453., 37244., 13672., 10290., 11167., 500.]])
        stats = parse.make_distributions(array_data)
        compare_stats = np.array([[5.387275e+04, 1.697478e+03],
                                  [3.442050e+04, 1.953430e+03],
                                  [1.348775e+04, 2.161880e+02],
                                  [1.021150e+04, 1.057080e+02],
                                  [1.116425e+04, 2.681000e+00],
                                  [5.000000e+02, 0.000000e+00]])
        assert (stats == compare_stats).all()
    def test_data_parse_3(self):
        # output parse file with a normal number of line segments on the MoorDyn files
        file_root = 'tests/test_fast/compare_output'
        ptfm_surge, ptfm_sway, anchor_tension, line1_tension, line2_tension, line3_tension = parse.output_parse(
            file_root)
        compare_ptfm_surge = np.array([[5.], [4.99989557], [4.9995923]])
        compare_line1_tension = np.array([[779500., 786500., 783300., 813300., 863200., 936800.],
                                          [779500., 786500., 783200., 813300., 863100., 936700.],
                                          [779500., 786500., 783200., 813400., 863000., 936600.],
                                          [779500., 786500., 783100., 813400., 862900., 936600.],
                                          [779500., 786500., 783100., 813400., 862800., 936700.],
                                          [779500., 786500., 783000., 813800., 862200., 936800.],
                                          [779500., 786500., 782900., 814100., 861700., 936900.],
                                          [779500., 786500., 782700., 813900., 861600., 937100.],
                                          [779500., 786500., 782700., 813400., 862200., 936900.]])
        assert (np.around(ptfm_surge, 3) == np.around(compare_ptfm_surge, 3)).all()
        assert (line1_tension == compare_line1_tension).all()

    def test_data_parse_4(self):
        # output parse file with 1 line segment on the MoorDyn files
        file_root = 'tests/test_fast/compare_output_1seg'
        ptfm_surge, ptfm_sway, anchor_tension, line1_tension, line2_tension, line3_tension = parse.output_parse(
            file_root, 1)
        compare_ptfm_surge = np.array([[5.], [4.99992895], [4.99972391]])
        compare_line1_tension = np.array([[0.], [0.], [0.], [0.], [0.], [0.], [0.], [0.], [0.]])
        assert (np.around(ptfm_surge, 3) == np.around(compare_ptfm_surge, 3)).all()
        assert (line1_tension == compare_line1_tension).all()


class TestFileCatching:
    def test_file_catching_1(self):
        # Test get_most_recent_file_containing functionality
        with open('file_catching_test_1_true_orig.txt', 'w') as file1:
            pass
        with open('file_catching_test_1_false.txt', 'w') as file2:
            pass
        time.sleep(1)
        with open('file_catching_test_1_true_later.txt', 'w') as file3:
            pass
        found_file = parse.get_most_recent_file_containing('file_catching_test_1_true', file_extension='.txt')
        compare_found_file = 'file_catching_test_1_true_later.txt'
        os.remove('file_catching_test_1_true_orig.txt')
        os.remove('file_catching_test_1_false.txt')
        os.remove('file_catching_test_1_true_later.txt')
        assert found_file == compare_found_file

    def test_file_catching_2(self):
        # Test get_filenames functionality
        test_dir = 'tests/test_data'
        txt_files = parse.get_filenames('.txt', file_directory=test_dir)
        compare_txt_files = ['test_currentdata_normal.txt', 'test_currentdata_overflow.txt',
                             'test_currentdata_string.txt', 'test_datetime_normal.txt', 'test_datetime_oldstyle.txt',
                             'test_datetime_skip.txt', 'test_metdata_normal.txt', 'test_metdata_overflow.txt',
                             'test_winddata_normal.txt', 'test_winddata_overflow.txt', 'test_winddata_realdata.txt']
        assert txt_files == compare_txt_files

    def test_file_catching_3(self):
        # Test move_files functionality
        file1_name = 'file_catching_test_3_a.txt'
        file2_name = 'file_catching_test_3_b.txt'
        destination_dir = 'tests/test_data'
        with open(file1_name, 'w') as file1:
            pass
        with open(file2_name, 'w') as file2:
            pass

        parse.move_files([file1_name, file2_name], destination_dir)
        assert os.path.isfile(destination_dir + '/' + file1_name)
        assert os.path.isfile(destination_dir + '/' + file2_name)
        os.remove(destination_dir + '/' + file1_name)
        os.remove(destination_dir + '/' + file2_name)

    def test_file_catching_4(self):
        # Test get_param_data with 1 parameter
        outb_file = 'tests/test_fast/test.outb'
        param = 'TTDspFA'
        data = parse.get_param_data(outb_file, [param])
        compare_data = np.array(
            [[-4.43845238e-16], [9.62318562e-04], [3.79391201e-03], [8.42924230e-03], [1.50089581e-02],
             [2.38785073e-02], [3.53180990e-02], [4.93474826e-02], [6.57844543e-02], [8.44349861e-02],
             [1.05165899e-01], [1.27794385e-01], [1.51940525e-01], [1.77067265e-01], [2.02668115e-01],
             [2.28349999e-01], [2.53716826e-01], [2.78226405e-01], [3.01222295e-01], [3.22121590e-01],
             [3.40536028e-01]])
        assert (np.round(data, 3) == np.round(compare_data, 3)).all()

    def test_file_catching_5(self):
        # Test get_param_data with multiple parameters
        outb_file = 'tests/test_fast/test.outb'
        params = ['TTDspFA', 'TTDspSS']
        data = parse.get_param_data(outb_file, params)
        compare_data = np.array([[-4.43845238e-16, -0.00000000e+00], [9.62318562e-04, -5.23049630e-06],
                                 [3.79391201e-03, -7.18154770e-05], [8.42924230e-03, -3.93483555e-04],
                                 [1.50089581e-02, -1.23804249e-03], [2.38785073e-02, -2.66403751e-03],
                                 [3.53180990e-02, -4.49600583e-03], [4.93474826e-02, -6.61688065e-03],
                                 [6.57844543e-02, -9.03512910e-03], [8.44349861e-02, -1.16145937e-02],
                                 [1.05165899e-01, -1.39949080e-02], [1.27794385e-01, -1.58704072e-02],
                                 [1.51940525e-01, -1.71847064e-02], [1.77067265e-01, -1.80325229e-02],
                                 [2.02668115e-01, -1.85418651e-02], [2.28349999e-01, -1.88985839e-02],
                                 [2.53716826e-01, -1.93320680e-02], [2.78226405e-01, -2.00219546e-02],
                                 [3.01222295e-01, -2.10917890e-02], [3.22121590e-01, -2.26534232e-02],
                                 [3.40536028e-01, -2.47239284e-02]])
        assert (np.round(data, 3) == np.round(compare_data, 3)).all()

    def test_file_catching_6(self):
        # Test get_moordyn_data with 1 parameter
        md_file = 'tests/test_fast/compare_output.MD.Line1.out'
        param = ['Seg5Ten']
        data = parse.get_moordyn_data(md_file, param)
        compare_data = np.array([[863200.], [863100.], [863000.],
                                 [862900.], [862800.], [862200.],
                                 [861700.], [861600.], [862200.]])
        assert (data == compare_data).all()


    def test_file_catching_7(self):
        # Test get_moordyn_data with multiple parameters
        md_file = 'tests/test_fast/compare_output.MD.Line1.out'
        params = ['Seg5Ten', 'Seg6Ten']
        data = parse.get_moordyn_data(md_file, params)
        compare_data = np.array([[863200., 936800.], [863100., 936700.], [863000., 936600.],
                                 [862900., 936600.], [862800., 936700.], [862200., 936800.],
                                 [861700., 936900.], [861600., 937100.], [862200., 936900.]])
        assert (data == compare_data).all()