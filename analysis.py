#!/usr/bin/python

import datetime
import pandas
import pandas.io.data
from   pandas import Series, DataFrame

import matplotlib

#################################################################
# analysis class
#################################################################
class analysis_class:
    """Analysis algorithms for stock indicators."""

    def __init__(self, scripid, date_start, date_end=datetime.datetime.now(), name=''):
        self.scripid         = scripid
        self.name            = ''
        self.date_start      = date_start
        self.date_end        = date_end
        self.stock_info      = pandas.io.data.get_data_yahoo(self.scripid, self.date_start, self.date_end)

        if self.name == '':
            self.name = self.scripid

    def moving_average(self, N):
        """Moving average for closing prices"""
        return pandas.rolling_mean(self.stock_info["Adj Close"], N)

    def accumulation_distribution(self):
        """Accumulation Distribution Data"""
        obj = self.stock_info.copy()
        return (obj["Close"] - obj["Open"])/(obj["High"] - obj["Low"]) * obj["Volume"]

    def volatility_index_single_pass(self, N):
        """This Volatility indicator is 1 pass and uses closing prices."""
        step_prev_list = self.stock_info["Adj Close"].copy()
        step_next_list = pandas.rolling_std(step_prev_list, N).dropna()
        return pandas.rolling_std(step_next_list, step_next_list.size)[-1]

    def volatility_index_multi_pass(self, N):
        """This volatility indicator is multipass and uses closing prices."""
        n = N
        step_prev_list = self.stock_info["Adj Close"].copy()
        while True:
            step_next_list = pandas.rolling_std(step_prev_list, n).dropna()
            if step_next_list.size < n:
                return step_next_list[-1]
            step_prev_list = step_next_list

    def volatility_index_multi_pass_expanding(self, N):
        """This volatility indicator is multipass and uses closing prices."""
        n = N
        step_prev_list = self.stock_info["Adj Close"].copy()
        while True:
            step_next_list = pandas.rolling_std(step_prev_list, n).dropna()
            n = n * 2
            if step_next_list.size < n:
                return step_next_list[-1]
            step_prev_list = step_next_list

    def print_info(self):
        """Print information about this class attributes."""
        print "name = {}, date_start = {}, date_end = {}" . format(self.name, self.date_start, self.date_end)

###############################################################################
# new plotting class library
###############################################################################
class plots_class:
    """Customized plotting class"""
    # Plot type constants
    PLOT_TYPE_BAR      = 0
    PLOT_TYPE_PLOT     = 1

    def __init__(self, label=''):
        """Initialize a new figure object."""
        self.fig       = matplotlib.pyplot.figure(label)
        self.data      = {}
        self.plotted   = 0
        self.n_columns = 1
        self.n_plots   = 0
        self.n_rows    = 0
        self.h_ratios  = []

    def new(self, n_plots, height_ratios=None, label=''):
        """Initialize the figure object. n_plots is the total number plots on this figure. \
                height_ratios is a tuple/list of the corresponding height ratios.The ratios should be integers only"""
        if height_ratios == None:
            height_ratios = [1] * n_plots

        assert(type(height_ratios) == tuple or type(height_ratios) == list)
        assert(len(height_ratios) == n_plots)
        # Clear figure
        self.fig.clf()

        self.h_ratios  = map(int, height_ratios)
        self.n_rows    = sum(self.h_ratios)
        self.n_plots   = n_plots
        self.n_columns = 1
        self.plotted   = 0
        self.__layout_subplots()

    def __layout_subplots(self):
        """Create layouts."""
        plot_obj_l     = []
        x              = 0
        for i in range(0, self.n_plots):
            plot_obj_l.append(matplotlib.pyplot.subplot2grid((self.n_rows, 1), (x, 0), rowspan=self.h_ratios[i]))
            x = x + self.h_ratios[i]
        self.plot_obj  = plot_obj_l

    def __inc_plotted(self):
        self.plotted   = self.plotted + 1

    def __append_new(self, ratio=1):
        """Make preparations for appending a new plot."""
        self.fig.clf()                           # Clear figure
        self.n_plots   = self.n_plots + 1        # Calculate new number of subplots
        self.h_ratios.append(ratio)              # Calculate new hratios
        self.n_rows    = sum(self.h_ratios)      # Calculate fresh number of rows
        self.__layout_subplots()                 # refresh previous layouts with new configuration
        self.plotted   = 0                       # reset plotted parameter

        # Draw previous plots again
        for i in range(0, (self.n_plots - 1)):
            for dict_this in self.data[i]:
                if dict_this["plot_type"] == self.PLOT_TYPE_PLOT:
                    self.__draw(i, dict_this["x_list"], dict_this["y_list"], dict_this["label"], self.PLOT_TYPE_PLOT)
                elif dict_this["plot_type"] == self.PLOT_TYPE_BAR:
                    self.__draw(i, dict_this["x_list"], dict_this["y_list"], dict_this["label"], self.PLOT_TYPE_BAR)
    
    def __check_valid_frame(self, ratio, frame):
        """Check if the frame is valid.If not, allocate a new frame."""
        if frame == None:
            if self.plotted >= self.n_plots:
                self.__append_new(ratio)
            return self.plotted
        else:
            assert(frame < self.n_plots)
            return frame

    def __append_data(self, frame, data):
        """Append the plot data structure to the object's internal database."""
        if not (frame in self.data):
            self.data[frame] = []
        self.data[frame].append(data)

    def __plot(self, obj, x_list, y_list, label):
        obj.plot(x_list, y_list, label=label)

    def __bar(self, obj, x_list, y_list, label):
        obj.bar(x_list, y_list, label=label)

    def __draw(self, frame, x_list, y_list, label, plot_type):
        """Internal plot."""
        obj_this       = self.plot_obj[frame]
        obj_this.grid()
        obj_this.set_title(label)
        if plot_type == self.PLOT_TYPE_PLOT:
            self.__plot(obj_this, x_list, y_list, label)
        elif plot_type == self.PLOT_TYPE_BAR:
            self.__bar(obj_this, x_list, y_list, label)
        self.fig.tight_layout()
        self.__inc_plotted()

    def plot(self, x_list, y_list, label='', ratio=1, frame=None):
        """Plot the actual data."""
        frame_new      = self.__check_valid_frame(ratio, frame)
        self.__draw(frame_new, x_list, y_list, label, self.PLOT_TYPE_PLOT)
        self.__append_data(frame_new,\
                  {"x_list" : x_list, "y_list" : y_list, "label" : label, "plot_type" : self.PLOT_TYPE_PLOT})
        

    def bar(self, x_list, y_list, label='', ratio=1, frame=None):
        """Plot the actual data as bars."""
        frame_new      = self.__check_valid_frame(ratio, frame)
        self.__draw(frame_new, x_list, y_list, label, self.PLOT_TYPE_BAR)
        self.__append_data(frame_new,\
                  {"x_list" : x_list, "y_list" : y_list, "label" : label, "plot_type" : self.PLOT_TYPE_BAR})

    def plot_pandas_series(self, series, label='', ratio=1, frame=None):
        """Plot pandas.core.series.Series type data."""
        assert(type(series) == pandas.core.series.Series)
        self.plot(series.index.tolist(), series.tolist(), label, ratio, frame)

    def bar_pandas_series(self, series, label='', ratio=1, frame=None):
        """Plot pandas.core.series.Series type data as bars."""
        assert(type(series) == pandas.core.series.Series)
        self.bar(series.index.tolist(), series.tolist(), label, ratio, frame)

