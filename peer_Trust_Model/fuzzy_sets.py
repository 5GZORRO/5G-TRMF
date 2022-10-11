from pyit2fls import T1FS, trapezoid_mf, T1FS_plot
from numpy import linspace
import matplotlib.pyplot as plt

#help(T1FS_plot)

def own_T1FS_plot(*sets, title=None, legends=None, filename=None,
                  ext="pdf", grid=True, xlabel="Domain", ylabel="Membership degree", n_colums=0):
    """
    Plots multiple T1FSs together in the same figure.

    Parameters
    ----------
    *sets:
        Multiple number of T1FSs which would be plotted.

    title:
        str

        If it is set, it indicates the title which would be
        represented in the plot. If it is not set, the plot would not
        have a title.

    legends:
        List of strs

        List of legend texts to be presented in plot. If it is not
        set, no legend would be in plot.

    filename:
        str

        If it is set, the plot would be saved as a filename.ext file.

    ext:
        str
        Extension of the output file with pdf default value.

    grid:
        bool
        Grid on/off.

    xlabel:
        str
        Label of the x axis.

    ylabel:
        str
        Label of the y axis.
    Examples
    --------

    domain = linspace(0., 1., 100)
    t1fs1 = T1FS(domain, gaussian_mf, [0.33, 0.2, 1.])
    t1fs2 = T1FS(domain, gaussian_mf, [0.66, 0.2, 1.])
    T1FS_plot(t1fs1, t1fs2, title="Plotting T1FSs",
                  legends=["First set", "Second set"])
    """

    plt.figure()
    for t1fs in sets:
        plt.plot(t1fs.domain, t1fs.mf(t1fs.domain, t1fs.params))
    if legends is not None:
        #plt.legend(legends, bbox_to_anchor=(1.04,1), loc="upper left")
        plt.legend(legends, bbox_to_anchor=(0,1.02,1,0.2), loc="upper left", mode="expand", ncol= n_colums)
        #plt.legend(["T(v,u)"], bbox_to_anchor=(-0.05,0.82,1,0.2), loc="lower right", mode="expand", ncol= 1)
    if title is not None:
        plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(grid)
    plt.plot([0.82,0.82],[0.0,0.84], 'k--')
    plt.plot([0,0.82],[0.84,0.84], 'k--')
    plt.text(0.77, 0.78, r'$\epsilon_1$')
    plt.plot([0,0.82],[0.16,0.16], 'k--')
    plt.text(0.77, 0.10, r'$\epsilon_2$')
    plt.text(0.81, -0.04, r'$T(v,u)$')
    #plt.plot([3,3],[0.0,0.739], 'k--')
    #plt.plot([0,3],[0.739,0.739], 'k--')
    #plt.text(2.76, 0.70, r'$\epsilon_3$')
    #plt.plot([0,3],[0.26,0.26], 'k--')
    #plt.text(2.76, 0.22, r'$\epsilon_4$')
    #plt.text(1.84, -0.04, r'$n$')
    #plt.text(3.66, -0.04, r'$2n$')
    #plt.text(5.50, -0.04, r'$3n$')
    #plt.arrow(0.82, 0.4, 0.05, -0.50, width=0.05, ec='black')
    if filename is not None:
        plt.savefig(filename + "." + ext, format=ext, dpi=300, bbox_inches="tight")
    plt.show()

def trust_fuzzy_set(trust_score):
    """This method leverages a trapzoidal function to determine the membership degree. The highest membership degree is selected"""
    domain = linspace(0., 0.175, 100)
    domain_1 = linspace(0.05, 0.425, 100)
    domain_2 = linspace(0.3, 0.675, 100)
    domain_3 = linspace(0.55, 0.925, 100)
    domain_4 = linspace(0.8, 1., 100)
    mySet = T1FS(domain, trapezoid_mf, [-1, 0., 0.05, 0.175, 1.])
    mySet_1 = T1FS(domain_1, trapezoid_mf, [0.05, 0.175, 0.3, 0.425, 1.])
    mySet_2 = T1FS(domain_2, trapezoid_mf, [0.3, 0.425, 0.55, 0.675, 1.])
    mySet_3 = T1FS(domain_3, trapezoid_mf, [0.55, 0.675, 0.8, 0.925, 1.])
    mySet_4 = T1FS(domain_4, trapezoid_mf, [0.8, 0.925, 1.05, 1.175, 1.])

    """own_T1FS_plot(mySet, mySet_1, mySet_2, mySet_3, mySet_4, legends=["Untrustworthy", "Little Trustworthy",
     "Moderately Trustworthy", "Trustworthy", "Full Trustworthy"], xlabel='Trust and Reputation values',
     filename='trust_levels', ext='pdf', n_colums=2)"""
    #print(trapezoid_mf(linspace(0.82, 0.82, 100), [0.55, 0.675, 0.8, 0.925, 1.]), trapezoid_mf(linspace(0.82, 0.82, 100), [0.8, 0.925, 1.05, 1.175, 1.]))

    if trust_score <= 0.175:
        untrustworthy = trapezoid_mf(linspace(trust_score, trust_score, 100), [-1, 0., 0.05, 0.175, 1.])
        little_trustworthy = trapezoid_mf(linspace(trust_score, trust_score, 100), [0.05, 0.175, 0.3, 0.425, 1.])
        if untrustworthy[0] > little_trustworthy[0]:
            return 0.2
        return 0.4
    elif trust_score > 0.175 and trust_score <= 0.425:
        little_trustworthy = trapezoid_mf(linspace(trust_score, trust_score, 100), [0.05, 0.175, 0.3, 0.425, 1.])
        moderately_trustworthy = trapezoid_mf(linspace(trust_score, trust_score, 100), [0.3, 0.425, 0.55, 0.675, 1.])
        if little_trustworthy[0] > moderately_trustworthy[0]:
            return 0.4
        return 0.6
    elif trust_score > 0.425 and trust_score < 0.675:
        moderately_trustworthy = trapezoid_mf(linspace(trust_score, trust_score, 100), [0.3, 0.425, 0.55, 0.675, 1.])
        trustworthy = trapezoid_mf(linspace(trust_score, trust_score, 100), [0.55, 0.675, 0.8, 0.925, 1.])
        if moderately_trustworthy[0] > trustworthy[0]:
            return 0.6
        return 0.8
    elif trust_score > 0.675 and trust_score < 0.925:
        trustworthy = trapezoid_mf(linspace(trust_score, trust_score, 100), [0.55, 0.675, 0.8, 0.925, 1.])
        full_trustworthy = trapezoid_mf(linspace(trust_score, trust_score, 100), [0.8, 0.925, 1.05, 1.175, 1.])
        if trustworthy[0] > full_trustworthy[0]:
            return 0.8
        return 1.0
    else:
        return 1.0


def violation_fuzzy_set(new_SLAViolations, historical_SLA_violation_rate):
    domain = linspace(0., historical_SLA_violation_rate, 100)
    domain_1 = linspace(historical_SLA_violation_rate/2, historical_SLA_violation_rate*2, 100)
    domain_2 = linspace(historical_SLA_violation_rate*1.5, historical_SLA_violation_rate*3, 100)

    mySet = T1FS(domain, trapezoid_mf, [-1, 0., historical_SLA_violation_rate/2, historical_SLA_violation_rate, 1.])
    mySet_1 = T1FS(domain_1, trapezoid_mf, [historical_SLA_violation_rate/2, historical_SLA_violation_rate, historical_SLA_violation_rate*1.5, historical_SLA_violation_rate*2, 1.])
    mySet_2 = T1FS(domain_2, trapezoid_mf, [historical_SLA_violation_rate*1.5, historical_SLA_violation_rate*2, historical_SLA_violation_rate*2.5, historical_SLA_violation_rate*3, 1.])

    #own_T1FS_plot(mySet, mySet_1, mySet_2, legends=["Momentary", "Recurrent", "Persistent"], xlabel='SLA violation rate', filename='SLAViolation_rate_levels', ext='pdf', n_colums=3)
    momentary = trapezoid_mf(linspace(new_SLAViolations, new_SLAViolations, 100), [-1, 0., historical_SLA_violation_rate/2, historical_SLA_violation_rate, 1.])
    recurrent= trapezoid_mf(linspace(new_SLAViolations, new_SLAViolations, 100), [historical_SLA_violation_rate/2, historical_SLA_violation_rate, historical_SLA_violation_rate*1.5, historical_SLA_violation_rate*2, 1.])
    persistent = trapezoid_mf(linspace(new_SLAViolations, new_SLAViolations, 100), [historical_SLA_violation_rate*1.5, historical_SLA_violation_rate*2, historical_SLA_violation_rate*2.5, historical_SLA_violation_rate*3, 1.])

    if int(momentary[0]) > 0 and recurrent[0] == 0:
        print(momentary, recurrent, persistent)
        return 1
    elif momentary[0] > 0 and recurrent[0] != 0:
        return 2
    elif recurrent[0] > 0 and persistent[0] == 0:
        return 2
    elif recurrent[0] > 0 and persistent[0] != 0:
        return 3
    elif persistent[0] > 0 and recurrent[0] == 0:
        return 3
    elif new_SLAViolations >= historical_SLA_violation_rate*3:
        return 3
