import matplotlib.pyplot as plt

def init_plot(radar_wavelength, two_radar=False):
    """
    Initializes the plot. If `two_radar` is True, creates a 1x2 subplot for two radars
    with lines for both co-polarization and cross-polarization.
    
    Parameters:
        radar_wavelength (str or tuple): Wavelength(s) to display in the title.
                                         If `two_radar` is True, provide a tuple (wavelength1, wavelength2).
        two_radar (bool): If True, creates a 1x2 subplot layout for two radar plots.
        
    Returns:
        fig (Figure): The Matplotlib figure object.
        ax (Axes or array of Axes): The Axes object(s) for plotting.
        lines (tuple): A tuple containing line objects for co-pol and cross-pol data.
                       If `two_radar` is True, returns two sets of lines.
    """
    plt.ion()  # Turn on interactive mode
    #fig, ax = plt.subplots(1, 2 if two_radar else 1, figsize=(12, 6))
    fig, ax = plt.subplots( 2 if two_radar else 1,1, figsize=(12, 6))
    if two_radar:
        # Unpack radar wavelengths
        wavelength1, wavelength2 = radar_wavelength
        
        # Initialize lines for each radar with co-pol and cross-pol
        line1_copol, = ax[0].plot([], [], 'r-', label="Co-Polarization")
        line1_crosspol, = ax[0].plot([], [], 'b-', label="Cross-Polarization")
        
        line2_copol, = ax[1].plot([], [], 'r-', label="Co-Polarization")
        line2_crosspol, = ax[1].plot([], [], 'b-', label="Cross-Polarization")
        
        # Set axis limits and titles
        ax[0].set_title(f"Radar 1 - {wavelength1}")
        ax[1].set_title(f"Radar 2 - {wavelength2}")
        
        for a in ax:
            
            if '17GHz' in a.get_title():
                a.set_ylim((0, 40000))
                a.set_xlim((0, 100))

            elif '13GHz' in a.get_title():
                a.set_ylim((0, 30000))
                a.set_xlim((0, 100))
                
            a.legend()
        return fig, ax, ((line1_copol, line1_crosspol), (line2_copol, line2_crosspol))
    
    else:
        # Single radar setup with co-pol and cross-pol lines
        line_copol, = ax.plot([], [], 'r-', label="Co-Polarization")
        line_crosspol, = ax.plot([], [], 'b-', label="Cross-Polarization")
        
        ax.set_title(f"Radar - {radar_wavelength}")
        # Set axis limits and title
        if '17GHz' in ax.get_title():
            ax.set_ylim((0, 40000))
            ax.set_xlim((0, 100))

        elif '13GHz' in ax.get_title():
            ax.set_ylim((0, 30000))
            ax.set_xlim((0, 100))

        # ax.set_ylim((0, 20000))
        # ax.set_xlim((0, 100))

        ax.legend()
        
        return fig, ax, (line_copol, line_crosspol)
    
def update_plot(ax, lines, rx_values_copol, rx_values_crosspol, two_radar=False, rx_values2_copol=None, rx_values2_crosspol=None):
    """
    Updates the plot with new data for co-polarization and cross-polarization.
    If `two_radar` is True, it updates two subplots with two lines each.
    
    Parameters:
        ax (Axes or array of Axes): The Axes object(s) for the subplots.
        lines (tuple): A tuple of line objects for co-pol and cross-pol. 
                       If `two_radar` is True, this should be ((line1_copol, line1_crosspol), (line2_copol, line2_crosspol)).
        rx_values_copol (list): Co-polarization data for radar 1.
        rx_values_crosspol (list): Cross-polarization data for radar 1.
        two_radar (bool): If True, updates the second radar plot as well.
        rx_values2_copol (list): Co-polarization data for radar 2 (optional, required if `two_radar` is True).
        rx_values2_crosspol (list): Cross-polarization data for radar 2 (optional, required if `two_radar` is True).
    """
    
    if two_radar:
        # Update Radar 1 lines
        line1_copol, line1_crosspol = lines[0]
        line1_copol.set_xdata(range(len(rx_values_copol)))
        line1_copol.set_ydata(rx_values_copol)
        line1_crosspol.set_xdata(range(len(rx_values_crosspol)))
        line1_crosspol.set_ydata(rx_values_crosspol)
        
        # Update Radar 2 lines
        line2_copol, line2_crosspol = lines[1]
        line2_copol.set_xdata(range(len(rx_values2_copol)))
        line2_copol.set_ydata(rx_values2_copol)
        line2_crosspol.set_xdata(range(len(rx_values2_crosspol)))
        line2_crosspol.set_ydata(rx_values2_crosspol)
        
        # Rescale and refresh each subplot
        ax[0].relim()
        ax[0].autoscale_view()
        ax[1].relim()
        ax[1].autoscale_view()
        
    else:
        # Single radar case
        line_copol, line_crosspol = lines
        line_copol.set_xdata(range(len(rx_values_copol)))
        line_copol.set_ydata(rx_values_copol)
        line_crosspol.set_xdata(range(len(rx_values_crosspol)))
        line_crosspol.set_ydata(rx_values_crosspol)
        
        # Rescale and refresh the single plot
        ax.relim()
        ax.autoscale_view()
    
    plt.draw()


# def init_plot():
#     plt.ion()
#     fig, (ax,ax2 = plt.subplots(1,2)
#     line_copol, = ax.plot([], [], 'r-')
#     line_crosspol, = ax.plot([], [], 'b-')
#     ax.set_ylim((0, 20000))
#     ax.set_xlim((0, 100))
    
#     line_copol, = ax.plot([], [], 'r-')
#     line_crosspol, = ax.plot([], [], 'b-')
#     ax.set_ylim((0, 20000))
#     ax.set_xlim((0, 100))
#     return fig, ax, line_copol, line_crosspol

# def update_plot(ax, line_copol, line_crosspol, rx_values_copol, rx_values_crosspol):
#     line_copol.set_xdata(range(len(rx_values_copol)))
#     line_copol.set_ydata(rx_values_copol)
#     line_crosspol.set_xdata(range(len(rx_values_crosspol)))
#     line_crosspol.set_ydata(rx_values_crosspol)
#     ax.relim()
#     ax.autoscale_view()
