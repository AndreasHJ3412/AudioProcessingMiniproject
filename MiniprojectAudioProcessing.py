import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk #GUI library
import sounddevice as sd #Sound library

class SynthesizerGUI:
    def __init__(self, master): #The constructor for the GUI class
        self.master = master #Sets the widget of the GUI. "self." refers to the instance of the class itself
        master.title("AudioProcessingSynthesizerMiniproject") #Set the title of the GUI

        # Initialize variables
        self.sampling_freq = 44100 #Default sampling frequency
        self.waveform = "Sine" #Sets the default waveform type to a sinewave
        self.frequency = "" #Makes the default frequency empty and ready for user input
        self.center_freq = 1000 #Default center frequency for resonator (Hz)
        self.resonance = 1.0 #Default resonance for resonator

        #GUI components
        #GUI frequency input
        self.frequency_label = tk.Label(master, text="Frequency (Hz):") #Creating a label for the frequency
        self.frequency_label.grid(row=0, column=0) #Places the frequency label widget
        self.frequency_input = tk.Entry(master) #Creates an space for user input
        self.frequency_input.insert(tk.END, str(self.frequency))  #Sets default frequency
        self.frequency_input.grid(row=0, column=1) #Places the frequency input widget

        # Resonator controls
        self.resonator_label = tk.Label(master, text="Resonator:")
        self.resonator_label.grid(row=1, column=0)
        self.center_freq_label = tk.Label(master, text="Center Frequency:")
        self.center_freq_label.grid(row=1, column=1)
        self.center_freq_entry = tk.Entry(master)
        self.center_freq_entry.insert(tk.END, str(self.center_freq))
        self.center_freq_entry.grid(row=1, column=2)
        self.resonance_label = tk.Label(master, text="Resonance:")
        self.resonance_label.grid(row=1, column=3)
        self.resonance_entry = tk.Entry(master)
        self.resonance_entry.insert(tk.END, str(self.resonance))
        self.resonance_entry.grid(row=1, column=4)

        # Waveform Selection
        self.waveform_label = tk.Label(master, text="Waveform:")
        self.waveform_label.grid(row=2, column=0)
        self.waveform_var = tk.StringVar()
        self.waveform_var.set("Sine") #Default waveform is set to Sine
        self.sine_button = tk.Radiobutton(master, text="Sine", variable=self.waveform_var, value="Sine",
                                          command=self.update_waveform)
        self.sine_button.grid(row=2, column=1)
        self.square_button = tk.Radiobutton(master, text="Square", variable=self.waveform_var, value="Square",
                                            command=self.update_waveform)
        self.square_button.grid(row=2, column=2)
        self.triangle_button = tk.Radiobutton(master, text="Triangle", variable=self.waveform_var, value="Triangle",
                                              command=self.update_waveform)
        self.triangle_button.grid(row=2, column=3)

        # Play Button
        self.play_button = tk.Button(master, text="Play", command=self.play_wave)
        self.play_button.grid(row=3, column=0,
                              columnspan=5)  #Places the "Play" button in the middle of the GUI

    #Makes a waveform based on the selected waveform type and frequency
    def generate_waveform(self):
        duration = 2  #Duration of the waveform in seconds
        t = np.linspace(0, duration, int(self.sampling_freq * duration), endpoint=False)

        #Make a waveform based on selected waveform type
        if self.waveform == 'Sine':
            wave = np.cos(2 * np.pi * self.frequency * t)  # Generate a sine wave
        elif self.waveform == 'Square':
            wave = np.sign(np.sin(2 * np.pi * self.frequency * t))  # Generate a square wave
        elif self.waveform == 'Triangle':
            wave = 2 * np.arcsin(np.sin(2 * np.pi * self.frequency * t)) / np.pi  # Generate a triangle wave

        return wave #Returns the generated waveform

    #Makes a resonator filter
    def resonator(self, center_freq, resonance, size):
        # Generate frequency response
        freqs = np.fft.fftfreq(size, 1 / self.sampling_freq) #Makes frequency samples
        response = 1 / (1 + (1j * (freqs / center_freq)) - ((freqs / center_freq) ** 2)) #Makes frequency response

        # Apply resonance
        response = response / np.max(np.abs(response)) #Normalize
        response = response ** resonance #Applies the resonance


        return np.real(np.fft.ifft(response)) #Compute inverse fast Fourier transform to change frequency  back to time domain only returning the real part

    def update_waveform(self):
        self.waveform = self.waveform_var.get() #Update the selected waveform

    #Play the generated waveform, create and display the waveform in a plot
    def play_wave(self):
        #Get frequency, center frequency and resonance from input
        self.frequency = float(self.frequency_input.get())
        self.center_freq = float(self.center_freq_entry.get())
        self.resonance = float(self.resonance_entry.get())

        #Make the waveform
        wave = self.generate_waveform()

        #Apply the resonator filter
        resonator_filter = self.resonator(self.center_freq, self.resonance, len(wave))
        filtered_wave = np.convolve(wave, resonator_filter, mode='same')

        #Play the sound
        sd.play(filtered_wave, self.sampling_freq)

        #Make a power spectrum of the waveform
        power_spectrum = np.abs(np.fft.fft(filtered_wave)) ** 2
        freqs = np.fft.fftfreq(len(filtered_wave), 1 / self.sampling_freq)

        #Show the waveform and power spectrum in plots
        plt.figure(figsize=(5, 3))
        plt.subplot(2, 1, 1)
        plt.plot(filtered_wave)

        #Set labels on the plots
        plt.title('Waveform after Resonator Filter')
        plt.xlabel('Sample')
        plt.ylabel('Amplitude')
        plt.xlim([0, 1000])  #Limit x-axis to show from 0 to 1000 to better see the waveform

        plt.subplot(2, 1, 2)
        plt.plot(freqs, 10 * np.log10(power_spectrum))
        plt.xlim([0, 1500])
        plt.ylim([-20, 100])
        plt.axvline(x=self.center_freq, color='r', linestyle='--')  #Add vertical line at center frequency
        plt.title('Power Spectrum after Resonator Filter')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power (dB)')

        plt.tight_layout()
        plt.show() #Show the plots

if __name__ == "__main__": #Only make program run when the script is run directly
    # Run the synthesizer application
    root = tk.Tk()  # Create the main Tkinter window
    app = SynthesizerGUI(root)  # Create an instance of the SynthesizerGUI class
    root.mainloop()  # Enter the Tkinter event loop to display the GUI and handle user interactions
