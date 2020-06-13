from fowt_force_gen import filegen
import filecmp
import os
import pandas as pd
import numpy as np


class TestFASTFileGen:
    def test_fast_filegen_1(self):
        # Test creating file with one parameter changed
        template_file = 'template_files/OC4Semi_OpenFAST_template.fst'
        new_file = 'fast_filegen_test_1.fst'
        compare_file = 'tests/test_fast/compare_fst_file_1.fst'
        filegen.filegen(template_file, new_file, TMax=50.5)
        assert filecmp.cmp(new_file, compare_file, shallow=False)
        os.remove(new_file)

    def test_fast_filegen_2(self):
        # Test creating file with two parameters changed
        template_file = 'template_files/OC4Semi_OpenFAST_template.fst'
        new_file = 'fast_filegen_test_2.fst'
        compare_file = 'tests/test_fast/compare_fst_file_2.fst'
        filegen.filegen(template_file, new_file, DT=0.05, AbortLevel='"SEVERE"')
        assert filecmp.cmp(new_file, compare_file, shallow=False)
        os.remove(new_file)

    def test_fast_filegen_3(self):
        # create fst file with (#) changes
        template_file = 'template_files/OC4Semi_OpenFAST_template.fst'
        new_file = 'fast_filegen_test_3.fst'
        compare_file = 'tests/test_fast/compare_fst_file_3.fst'
        filegen.filegen(template_file, new_file, BDBldFile={'1': 'file1', '3': 'file3'})
        assert filecmp.cmp(new_file, compare_file, shallow=False)
        os.remove(new_file)

    def test_fast_filegen_4(self):
        # create moordyn_filegen with horizontal parameter changes
        template_file = 'template_files/OC3Hywind_MoorDyn_rough_template.dat'
        new_file = 'md_filegen_test_1.dat'
        compare_file = 'tests/test_fast/compare_md_file_1.dat'
        filegen.moordyn_filegen(template_file, new_file, TmaxIC=150)
        assert filecmp.cmp(new_file, compare_file, shallow=False)
        os.remove(new_file)

    def test_fast_filegen_5(self):
        # create moordyn_filegen with both horizontal and vertical parameter changes
        template_file = 'template_files/OC3Hywind_MoorDyn_rough_template.dat'
        new_file = 'md_filegen_test_2.dat'
        compare_file = 'tests/test_fast/compare_md_file_2.dat'
        filegen.moordyn_filegen(template_file, new_file, dtIC=1.2, Type={'1': 'vessel', '2': 'vessel', '5': 'fixed'})
        assert filecmp.cmp(new_file, compare_file, shallow=False)
        os.remove(new_file)


class TestBulkFile:
    def test_bulk_file_1(self):
        # inp bulk filegen with two test files
        template_file = 'template_files/IECKAI_template.inp'
        new_file_root = 'test_inp'
        expected_file1 = 'test_inp_10mps_IECKAI.inp'
        expected_file2 = 'test_inp_11.4mps_IECKAI.inp'
        compare_file1 = 'tests/test_fast/compare_inp_10mps_IECKAI.inp'
        compare_file2 = 'tests/test_fast/compare_inp_11.4mps_IECKAI.inp'
        speeds = [10, 11.4]
        filegen.inp_bulk_filegen(template_file, new_file_root, speeds)
        assert os.path.isfile(expected_file1)
        assert os.path.isfile(expected_file2)
        assert filecmp.cmp(expected_file1, compare_file1, shallow=False)
        assert filecmp.cmp(expected_file2, compare_file2, shallow=False)
        os.remove(expected_file1)
        os.remove(expected_file2)

    def test_bulk_file_2(self):
        # inflowwind bulk filegen with two test files
        template_file = 'template_files/InflowWind_template.dat'
        new_file_root = 'test_ifw'
        expected_file1 = 'test_ifw_10mps_0deg.dat'
        expected_file2 = 'test_ifw_10mps_180deg.dat'
        expected_file3 = 'test_ifw_11.4mps_0deg.dat'
        expected_file4 = 'test_ifw_11.4mps_180deg.dat'
        compare_file1 = 'tests/test_fast/compare_inflowwind_10mps_0deg.dat'
        compare_file2 = 'tests/test_fast/compare_inflowwind_10mps_180deg.dat'
        compare_file3 = 'tests/test_fast/compare_inflowwind_11.4mps_0deg.dat'
        compare_file4 = 'tests/test_fast/compare_inflowwind_11.4mps_180deg.dat'
        directions = [0, 180]
        filegen.inflowwind_bulk_filegen(template_file, new_file_root, 'tests/test_fast', directions)
        assert os.path.isfile(expected_file1)
        assert os.path.isfile(expected_file2)
        assert os.path.isfile(expected_file3)
        assert os.path.isfile(expected_file4)
        assert filecmp.cmp(expected_file1, compare_file1, shallow=False)
        assert filecmp.cmp(expected_file2, compare_file2, shallow=False)
        assert filecmp.cmp(expected_file3, compare_file3, shallow=False)
        assert filecmp.cmp(expected_file4, compare_file4, shallow=False)
        os.remove(expected_file1)
        os.remove(expected_file2)
        os.remove(expected_file3)
        os.remove(expected_file4)

    def test_bulk_file_3(self):
        # hydrodyn_bulk_filegen for given water depth, wave climate, and current climate
        template_file = 'template_files/OC4Semi_HydroDyn_template.dat'
        new_file_root = 'test_hd'
        expected_file1 = 'test_hd_Climate0.dat'
        expected_file2 = 'test_hd_Climate1.dat'
        compare_file1 = 'tests/test_fast/compare_hydrodyn_Climate0.dat'
        compare_file2 = 'tests/test_fast/compare_hydrodyn_Climate1.dat'
        water_depth = '200'
        wave_climates = pd.DataFrame(data={'Significant Wave Height': [5, 10], 'Wave Direction': [20, -145],
                                           'Wave Period': [5.5838, 9.5837]})
        current_climate = [5.5, 3.4, -20]
        filegen.hydrodyn_bulk_filegen(template_file, new_file_root, water_depth, wave_climates, current_climate)
        assert os.path.isfile(expected_file1)
        assert os.path.isfile(expected_file2)
        assert filecmp.cmp(expected_file1, compare_file1, shallow=False)
        assert filecmp.cmp(expected_file2, compare_file2, shallow=False)
        os.remove(expected_file1)
        os.remove(expected_file2)

    def test_bulk_file_5(self):
        # fst_bulk_filegen for two test files
        template_file = 'template_files/OC4Semi_OpenFAST_template.fst'
        new_file_root = 'test_fst'
        moordyn_file = 'tests/test_fast/compare_md_file_1.dat'
        ifw_file_dir = 'tests/test_fast/test_fst_bulk'
        hd_file_dir = 'tests/test_fast/test_fst_bulk'
        expected_file1 = 'test_fst_10mps_0deg_Climate0.fst'
        expected_file2 = 'test_fst_10mps_0deg_Climate1.fst'
        expected_file3 = 'test_fst_11.4mps_180deg_Climate0.fst'
        expected_file4 = 'test_fst_11.4mps_180deg_Climate1.fst'
        compare_file1 = 'tests/test_fast/compare_fst_bulk_10mps_0deg_Climate0.fst'
        compare_file2 = 'tests/test_fast/compare_fst_bulk_10mps_0deg_Climate1.fst'
        compare_file3 = 'tests/test_fast/compare_fst_bulk_11.4mps_180deg_Climate0.fst'
        compare_file4 = 'tests/test_fast/compare_fst_bulk_11.4mps_180deg_Climate1.fst'
        filegen.fst_bulk_filegen(template_file, new_file_root, moordyn_file, ifw_file_dir, hd_file_dir)
        assert os.path.isfile(expected_file1)
        assert os.path.isfile(expected_file2)
        assert os.path.isfile(expected_file3)
        assert os.path.isfile(expected_file4)
        assert filecmp.cmp(expected_file1, compare_file1, shallow=False)
        assert filecmp.cmp(expected_file2, compare_file2, shallow=False)
        assert filecmp.cmp(expected_file3, compare_file3, shallow=False)
        assert filecmp.cmp(expected_file4, compare_file4, shallow=False)
        os.remove(expected_file1)
        os.remove(expected_file2)
        os.remove(expected_file3)
        os.remove(expected_file4)

    def test_bulk_file_6(self):
        # create_mat_files TODO: make it so the header is ignored so you can do an actual compared assertion
        surge_stats = np.array([11.502, 1.054])
        sway_stats = np.array([3.402, 0.551])
        anchor_stats = np.array([[6.1249e+04, 1.697478e+03],
                                 [6.1249e+04, 1.953430e+03],
                                 [2.4295e+04, 1.24845e+02]])
        line1_stats = np.array([[5.387275e+04, 1.697478e+03],
                                [3.442050e+04, 1.953430e+03],
                                [1.348775e+04, 2.161880e+02],
                                [1.021150e+04, 1.057080e+02],
                                [1.116425e+04, 2.681000e+00],
                                [5.000000e+02, 0.000000e+00]])
        line2_stats = np.array([[4.42145e+04, 1.423178e+03],
                                [3.442050e+04, 1.5325630e+03],
                                [1.3463825e+04, 2.64390e+02],
                                [1.0421850e+04, 1.32980e+02],
                                [1.14285e+04, 2.5328000e+00],
                                [4.000000e+02, 0.000000e+00]])
        line3_stats = np.array([[5.341275e+04, 1.697478e+03],
                                [3.4421850e+04, 1.42430e+03],
                                [1.345935e+04, 2.42880e+02],
                                [1.0242180e+04, 1.42980e+02],
                                [1.114281e+04, 2.421900e+00],
                                [4.000000e+02, 0.000000e+00]])

        new_rel_mat_file = 'rel_test.mat'
        new_surge_mat_file = 'surge_test.mat'
        filegen.create_mat_files(new_rel_mat_file, new_surge_mat_file,
                                 line1_stats, line2_stats, line3_stats, anchor_stats[0, :], anchor_stats[1, :],
                                 anchor_stats[2, :], surge_stats, sway_stats)
        assert os.path.isfile(new_rel_mat_file)
        assert os.path.isfile(new_surge_mat_file)
        os.remove(new_rel_mat_file)
        os.remove(new_surge_mat_file)