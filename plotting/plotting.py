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
        line1_copol, = ax[0].plot([], [], 'b-', label="Co-Polarization")
        line1_crosspol, = ax[0].plot([], [], 'r-', label="Cross-Polarization")
        dashline1_copol, = ax[0].plot([], [], 'b--', label="Recorded Co-Polarization")
        dashline1_crosspol, = ax[0].plot([], [], 'r--', label="Recorded Cross-Polarization")
        
        
        line2_copol, = ax[1].plot([], [], 'b-', label="Co-Polarization")
        line2_crosspol, = ax[1].plot([], [], 'r-', label="Cross-Polarization")
        dashline2_copol, = ax[1].plot([], [], 'b--', label="Recorded Co-Polarization")
        dashline2_crosspol, = ax[1].plot([], [], 'r--', label="Recorded Cross-Polarization")
        
        # Set axis limits and titles
        ax[0].set_title(f"Radar 1 - {wavelength1}")
        ax[1].set_title(f"Radar 2 - {wavelength2}")
        
        for a in ax:
            
            if '17GHz' in a.get_title():
                a.set_ylim((0, 60000))
                a.set_xlim((0, 100))

            elif '13GHz' in a.get_title():
                a.set_ylim((0, 60000))
                a.set_xlim((0, 100))
                
            a.legend()
        return fig, ax, ((line1_copol, line1_crosspol), 
                         (line2_copol, line2_crosspol)), ((dashline1_copol,dashline1_crosspol),
                                                          (dashline2_copol,dashline2_crosspol))


    else:
        # Single radar setup with co-pol and cross-pol lines
        line_copol, = ax.plot([], [], 'b-', label="Co-Polarization")
        line_crosspol, = ax.plot([], [], 'r-', label="Cross-Polarization")
        dashline_copol, = ax.plot([], [], 'b--', label="Recorded Co-Polarization")
        dashline_crosspol, = ax.plot([], [], 'r--', label="Recorded Cross-Polarization")    
        
        ax.set_title(f"Radar - {radar_wavelength}")
        # Set axis limits and title
        if '17GHz' in ax.get_title():
            ax.set_ylim((0, 60000))
            ax.set_xlim((0, 100))

        elif '13GHz' in ax.get_title():
            ax.set_ylim((0, 60000))
            ax.set_xlim((0, 100))

        # ax.set_ylim((0, 20000))
        # ax.set_xlim((0, 100))

        ax.legend()
        
        return fig, ax, (line_copol, line_crosspol), (dashline_copol, dashline_crosspol)
    
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
        line1_crosspol, line1_copol = lines[0]
        #line1_copol, line1_crosspol = lines[0]
        line1_copol.set_xdata(range(len(rx_values_copol)))
        line1_copol.set_ydata(rx_values_copol)
        line1_crosspol.set_xdata(range(len(rx_values_crosspol)))
        line1_crosspol.set_ydata(rx_values_crosspol)
        
        # Update Radar 2 lines
        line2_crosspol, line2_copol = lines[1]
        line2_copol.set_xdata(range(len(rx_values2_copol)))
        line2_copol.set_ydata(rx_values2_copol)
        line2_crosspol.set_xdata(range(len(rx_values2_crosspol)))
        line2_crosspol.set_ydata(rx_values2_crosspol)
        
        # Rescale and refresh each subplot
        for a in ax:
            a.relim()
            a.autoscale_view()
        
    else:
        # Single radar case
        line_crosspol, line_copol = lines
        #line_copol, line_crosspol = lines
        line_copol.set_xdata(range(len(rx_values_copol)))
        line_copol.set_ydata(rx_values_copol)
        line_crosspol.set_xdata(range(len(rx_values_crosspol)))
        line_crosspol.set_ydata(rx_values_crosspol)
        
        # Rescale and refresh the single plot
        ax.relim()
        ax.autoscale_view()
    
    plt.draw()

def update_record_plot(ax, dashlines, rx_values_copol, rx_values_crosspol, 
                       two_radar=False, measure_type=None, rx_values2_copol=None, rx_values2_crosspol=None, ):
    """
    Updates the plot with recorded data for co-polarization and cross-polarization.
    If `two_radar` is True, it updates two subplots with two dashed lines each.

    Parameters:
        ax (Axes or array of Axes): The Axes object(s) for the subplots.
        dashlines (tuple): A tuple of dashed line objects for recorded co-pol and cross-pol. 
                           If `two_radar` is True, this should be ((dashline1_copol, dashline1_crosspol), (dashline2_copol, dashline2_crosspol)).
        rx_values_copol (list): Recorded co-polarization data for radar 1.
        rx_values_crosspol (list): Recorded cross-polarization data for radar 1.
        two_radar (bool): If True, updates the second radar plot as well.
        rx_values2_copol (list): Recorded co-polarization data for radar 2 (optional, required if `two_radar` is True).
        rx_values2_crosspol (list): Recorded cross-polarization data for radar 2 (optional, required if `two_radar` is True).
    """
    #print(dashlines)
    if two_radar and measure_type == 'both':
        # Update Radar 1 lines
        line1_crosspol, line1_copol = dashlines[0]
        #line1_copol, line1_crosspol = dashlines[0]
        line1_copol.set_xdata(range(len(rx_values_copol)))
        line1_copol.set_ydata(rx_values_copol)
        line1_crosspol.set_xdata(range(len(rx_values_crosspol)))
        line1_crosspol.set_ydata(rx_values_crosspol)
        
        # Update Radar 2 lines
        line2_crosspol, line2_copol = dashlines[1]
        #line2_copol, line2_crosspol = dashlines[1]
        line2_copol.set_xdata(range(len(rx_values2_copol)))
        line2_copol.set_ydata(rx_values2_copol)
        line2_crosspol.set_xdata(range(len(rx_values2_crosspol)))
        line2_crosspol.set_ydata(rx_values2_crosspol)
        
        # Rescale and refresh each subplot
        for a in ax:
            a.relim()
            a.autoscale_view()
            
    elif two_radar and measure_type == '13GHz':
        # Update Radar 1 lines
        line1_crosspol, line1_copol = dashlines[0]
        #line1_copol, line1_crosspol = dashlines[0]
        line1_copol.set_xdata(range(len(rx_values_copol)))
        line1_copol.set_ydata(rx_values_copol)
        line1_crosspol.set_xdata(range(len(rx_values_crosspol)))
        line1_crosspol.set_ydata(rx_values_crosspol)
        
        ax[0].relim()
        ax[0].autoscale_view()

    elif two_radar and measure_type == '17GHz':
        # Update Radar 1 lines
        line2_crosspol, line2_copol = dashlines[1]
        #line2_copol, line2_crosspol = dashlines[1]
        line2_copol.set_xdata(range(len(rx_values_copol)))
        line2_copol.set_ydata(rx_values_copol)
        line2_crosspol.set_xdata(range(len(rx_values_crosspol)))
        line2_crosspol.set_ydata(rx_values_crosspol)
        
        ax[1].relim()
        ax[1].autoscale_view()
        
        
    else:
        # Single radar case
        line_crosspol, line_copol = dashlines
        #line_copol, line_crosspol = dashlines
        line_copol.set_xdata(range(len(rx_values_copol)))
        line_copol.set_ydata(rx_values_copol)
        line_crosspol.set_xdata(range(len(rx_values_crosspol)))
        line_crosspol.set_ydata(rx_values_crosspol)
        
        # Rescale and refresh the single plot
        ax.relim()
        ax.autoscale_view()
    
    plt.draw()
    