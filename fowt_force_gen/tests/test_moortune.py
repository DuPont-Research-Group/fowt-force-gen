from fowt_force_gen import moortune
import numpy as np
import filecmp
import os


class TestAnchorVal:
    def test_anchor_val_1(self):
        # Test positions for OC3
        mooring = moortune.Mooring(200, 'oc3')
        compare_anchor_x = np.array([4888.141, -2444.071, -2444.071])
        compare_anchor_y = np.array([0., 4233.251, -4233.251])
        assert (mooring.anchor_x == compare_anchor_x).all()
        assert (mooring.anchor_y == compare_anchor_y).all()

    def test_anchor_val_2(self):
        # Test anchor positions for OC4
        mooring = moortune.Mooring(200, 'oc4')
        compare_anchor_x = np.array([1762.549, -3525.098, 1762.549])
        compare_anchor_y = np.array([3052.824, 0., -3052.824])
        assert (mooring.anchor_x == compare_anchor_x).all()
        assert (mooring.anchor_y == compare_anchor_y).all()


class TestRoughTune:
    def test_rough_tune_1(self):
        # Test initial line length calculation
        mooring = moortune.Mooring(200, 'oc4')
        line_length = mooring.get_initial_line_length()
        compare_line_length = 3491.871
        assert line_length == compare_line_length

    def test_rough_tune_2(self):
        # Test OpenFAST input file creation for rough tuning
        mooring = moortune.Mooring(200, 'oc4')
        line_length = mooring.get_initial_line_length()
        mooring.update_tuning_inputs(line_length, test='rough')
        assert filecmp.cmp('rough_temp.fst', 'tests/test_fast/compare_tune_rough.fst')
        assert filecmp.cmp('moordyn_temp.dat', 'tests/test_fast/compare_tune_rough_moordyn.dat')
        assert filecmp.cmp('hydrodyn_rough_temp.dat', 'tests/test_fast/compare_tune_rough_hydrodyn.dat')
        os.remove('moordyn_temp.dat')
        os.remove('hydrodyn_rough_temp.dat')
        os.remove('rough_temp.fst')

    def test_rough_tune_3(self):
        # Test true condition for rough tuning check
        mooring = moortune.Mooring(200, 'oc4')
        assert mooring.check_rough_tuning('tests/test_fast/compare_tune_rough_nouplift.outb')

    def test_rough_tune_4(self):
        # Test false condition for rough tuning check
        mooring = moortune.Mooring(200, 'oc4')
        assert mooring.check_rough_tuning('tests/test_fast/compare_tune_rough_uplift.outb') is False


class TestFineTune:
    def test_fine_tune_1(self):
        # Test baseline decay data generation
        mooring = moortune.Mooring(200, 'oc4')
        baseline_time, baseline_surge = mooring.get_decay_data(mooring.baseline_outb_file)
        compare_baseline_time = np.arange(300.05, step=.05)
        compare_baseline_surge = np.genfromtxt('tests/test_data/compare_baseline_surge.csv', delimiter=',')
        assert (baseline_time == compare_baseline_time).all()
        assert (baseline_surge == compare_baseline_surge).all()

    def test_fine_tune_2(self):
        # Test OpenFAST input file creation for fine tuning
        mooring = moortune.Mooring(200, 'oc4')
        line_length = mooring.get_initial_line_length()
        mooring.update_tuning_inputs(line_length, test='fine', md_filename='moordyn_temp.dat')
        assert filecmp.cmp('fine_temp.fst', 'tests/test_fast/compare_tune_fine.fst')
        assert filecmp.cmp('moordyn_temp.dat', 'tests/test_fast/compare_tune_fine_moordyn.dat')
        assert filecmp.cmp('hydrodyn_fine_temp.dat', 'tests/test_fast/compare_tune_fine_hydrodyn.dat')
        os.remove('moordyn_temp.dat')
        os.remove('hydrodyn_fine_temp.dat')
        os.remove('fine_temp.fst')

    def test_fine_tune_3(self):
        # Test zero crossing identification for a test with the same number of crossings as baseline
        mooring = moortune.Mooring(200, 'oc4')
        baseline_time, baseline_surge = mooring.get_decay_data(mooring.baseline_outb_file)
        test_time, test_surge = mooring.get_decay_data('tests/test_fast/compare_tune_fine_samecrossings.outb')
        error = mooring.compare_zero_crossings(baseline_time, test_time, baseline_surge, test_surge)
        compare_error = np.array([-0.4, -0.25, -0.1, 0.15, 0.3])
        assert (np.around(error, 3) == compare_error).all()

    def test_fine_tune_4(self):
        # Test zero crossing identification for a test with more crossings than baseline
        mooring = moortune.Mooring(200, 'oc4')
        baseline_time, baseline_surge = mooring.get_decay_data(mooring.baseline_outb_file)
        test_time, test_surge = mooring.get_decay_data('tests/test_fast/compare_tune_fine_morecrossings.outb')
        error = mooring.compare_zero_crossings(baseline_time, test_time, baseline_surge, test_surge)
        print(error)
        compare_error = np.array([12.3, 37.2, 59.2, 81.8, 103.85])
        assert (np.around(error, 3) == compare_error).all()

    def test_fine_tune_5(self):
        # Test zero crossing identification for a test with less crossings than baseline
        mooring = moortune.Mooring(200, 'oc4')
        baseline_time, baseline_surge = mooring.get_decay_data(mooring.baseline_outb_file)
        test_time, test_surge = mooring.get_decay_data('tests/test_fast/compare_tune_fine_fewercrossings.outb')
        error = mooring.compare_zero_crossings(baseline_time, test_time, baseline_surge, test_surge)
        compare_error = np.array([-110.85])
        assert (np.around(error, 3) == compare_error).all()

    def test_fine_tune_6(self):
        # Test true condition for fine tuning check
        mooring = moortune.Mooring(200, 'oc4')
        prev_max_errors = [20., 16., 12., 8., 4.]
        freq_error = [-.2, .05, -.5, .042, .34]
        tuned, line_adjust = mooring.check_fine_tuning(freq_error, prev_max_errors)
        compare_tuned = True
        compare_line_adjust = 0
        assert tuned == compare_tuned
        assert line_adjust == compare_line_adjust

    def test_fine_tune_7(self):
        # Test false condition for fine tuning check with positive line_adjust
        mooring = moortune.Mooring(200, 'oc4')
        prev_max_errors = [20., 16., 12., 8., 4.]
        freq_error = [22., 14., -10., 8., -5.]
        tuned, line_adjust = mooring.check_fine_tuning(freq_error, prev_max_errors)
        compare_tuned = False
        compare_line_adjust = 1.571
        assert tuned == compare_tuned
        assert line_adjust == compare_line_adjust

    def test_fine_tune_8(self):
        # Test false condition for fine tuning check with negative line_adjust
        mooring = moortune.Mooring(200, 'oc4')
        prev_max_errors = [20., 16., 12., 8., 4.]
        freq_error = [-5., 2., -1., 2.5, 4.5]
        tuned, line_adjust = mooring.check_fine_tuning(freq_error, prev_max_errors)
        compare_tuned = False
        compare_line_adjust = -.5
        assert tuned == compare_tuned
        assert line_adjust == compare_line_adjust

    def test_fine_tune_9(self):
        # Test false condition for fine tuning check with flipflop_error
        mooring = moortune.Mooring(200, 'oc4')
        prev_max_errors = [20., 16., 12., 8., 4.]
        freq_error = [12., 2., -1., 2.5, 3.5]
        tuned, line_adjust = mooring.check_fine_tuning(freq_error, prev_max_errors)
        compare_tuned = False
        compare_line_adjust = 2.
        assert tuned == compare_tuned
        assert line_adjust == compare_line_adjust