const { app, BrowserWindow, Tray, Menu, screen } = require('electron');
const path = require('path');

let win;
let tray;

function createWindow() {
  win = new BrowserWindow({
    width: 300,
    height: 200,
    frame: false,
    transparent: false,
    alwaysOnTop: true,
    resizable: false,
    skipTaskbar: true,
    show: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  win.setPosition(width - 300, height - 200);
  win.loadFile('index.html');

  // Prevent window from closing — hide instead
  win.on('close', (event) => {
    event.preventDefault();
    win.hide();
  });
}

function toggleWindow() {
  if (!win) return;

  if (win.isVisible()) {
    win.hide();
  } else {
    win.show();
    win.focus(); // optional: bring to front
  }
}

function createTray() {
  tray = new Tray(path.join(__dirname, 'temptrayimg.ico'));

  const contextMenu = Menu.buildFromTemplate([
    { label: 'Toggle Window', click: toggleWindow },
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() }
  ]);

  tray.setToolTip('Popup Game');
  tray.setContextMenu(contextMenu);
  tray.on('click', toggleWindow); // single-click to toggle
}

app.whenReady()
  .then(() => {
    createWindow();
    createTray();
  })
  .catch(err => {
    console.error('Startup error:', err);
  });

// Keep app running even when windows are closed
app.on('window-all-closed', (e) => {
  e.preventDefault();
});