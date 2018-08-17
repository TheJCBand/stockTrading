import pandas
import matplotlib.pyplot as plt

perf = pandas.read_pickle('RSIBBData.pickle') # read in perf DataFrame
perf.head()

%pylab inline
figsize(12, 12)

ax1 = plt.subplot(211)
perf.portfolio_value.plot(ax=ax1)
ax1.set_ylabel('portfolio value')
ax2 = plt.subplot(212, sharex=ax1)
perf.leverage.plot(ax=ax2)
ax2.set_ylabel('Account Leverage')