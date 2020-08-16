package main

import (
  "os"
  "os/signal"
  "syscall"
  "fmt"
  "time"
  ws2811 "github.com/rpi-ws281x/rpi-ws281x-go"
)

const (
  brightness = 255
  ledCounts  = 150
)

type wsEngine interface {
  Init() error
  Render() error
  Wait() error
  Fini()
  Leds(channel int) []uint32
}

func checkError(err error) {
  if err != nil {
    panic(err)
  }
}

type colorWipe struct {
  ws wsEngine
}

func (cw *colorWipe) setup() error {
  return cw.ws.Init()
}

// Loop through each led individually and render instantly led per led:
func (cw *colorWipe) display(color uint32) error {
  for i := 0; i < len(cw.ws.Leds(0)); i++ {
    cw.ws.Leds(0)[i] = color
    if err := cw.ws.Render(); err != nil {
      return err
    }
  }
  return nil
}

// Loop through each led individually and render only after all leds are set:
func (cw *colorWipe) displayFlash(color uint32) error {
  for i := 0; i < len(cw.ws.Leds(0)); i++ {
    cw.ws.Leds(0)[i] = color
  }
  if err := cw.ws.Render(); err != nil {
    return err
  }
  return nil
}

var (
//  sleepTime time.Duration = 250 * time.Millisecond
  sleepTime time.Duration = 1 * time.Second
)

func main() {
  // set up a signal handler to catch Ctrl-C
  sig := make(chan os.Signal)
  signal.Notify(sig, os.Interrupt, syscall.SIGTERM)
  stopLoop := false

  opt := ws2811.DefaultOptions
  opt.Channels[0].StripeType = ws2811.SK6812WStrip
  opt.Channels[0].Brightness = brightness
  opt.Channels[0].LedCount = ledCounts

  dev, err := ws2811.MakeWS2811(&opt)
  checkError(err)

  cw := &colorWipe{
    ws: dev,
  }
  checkError(cw.setup())
  defer dev.Fini()

  // Handle Ctrl-C (stop looping)
  go func(){
    <-sig
    fmt.Println("stopping...")
    stopLoop = true
  }()

  // Endless cycle through led settings:
  for {
    // The uint32 data type goes to 4294967295 -> 0xFFFFFFFF
//    cw.display(uint32(0xff000000))  // native white led (W)
//    if stopLoop { break }
//    cw.display(uint32(0x00ffffff))  // composite white (RGB)
//    if stopLoop { break }
//    cw.display(uint32(0xffffffff))  // native white + composite white (RGBW)
//    if stopLoop { break }

    cw.displayFlash(uint32(0xff000000))  // native white led (W)
    time.Sleep(sleepTime)
    if stopLoop { break }
// Composite white does not look very nice
//    cw.displayFlash(uint32(0x00ffffff))  // composite white (RGB)
//    time.Sleep(sleepTime)
//    if stopLoop { break }

    cw.displayFlash(uint32(0xffffffff))  // native white + composite white (RGBW)
    time.Sleep(sleepTime)
    if stopLoop { break }
  }
  // This code will get executed after Ctrl-C is pressed
  cw.displayFlash(uint32(0x00000000))    // all off
}
