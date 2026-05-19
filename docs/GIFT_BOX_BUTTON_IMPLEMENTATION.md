# Gift Box Button Implementation Guide

This document describes how the gift box button (present button) is implemented in the main menu of Plants vs. Zombies C++ version.

## Overview

The gift box button (`mPresentButton`) is a `NewLawnButton` widget added to the `GameSelector` class. It uses the `IMAGE_PRESENT` image resource and triggers the opening of a custom widget (`MyWidget`) when clicked.

## Code Locations and Implementation

### 1. Header Declaration

**File**: `src/Lawn/Widget/GameSelector.h`

**Location**: Line 87

```cpp
NewLawnButton*              mPresentButton;             // 礼盒按钮 (Gift box button)
```

**Description**: 
- Declares the gift box button as a member variable of the `GameSelector` class
- Type: `NewLawnButton*`
- Comment indicates it's the gift box button

### 2. Button ID Definition

**File**: `src/Lawn/Widget/GameSelector.h`

**Location**: Lines 51-69

```cpp
private:
    enum
    {
        GameSelector_Adventure = 100,
        GameSelector_Minigame = 101,
        GameSelector_Puzzle = 102,
        GameSelector_Options = 103,
        GameSelector_Help = 104,
        GameSelector_Quit = 105,
        GameSelector_ChangeUser = 106,
        GameSelector_Store = 107,
        GameSelector_Almanac = 108,
        GameSelector_ZenGarden = 109,
        GameSelector_Survival = 110,
        GameSelector_Zombatar = 111,
        GameSelector_AchievementsBack = 112,
        GameSelector_Achievements = 113,
        GameSelector_QuickPlay = 114,
        GameSelector_Present = 115    // Gift box button ID
    };
```

**Description**:
- Defines the button ID as `GameSelector_Present = 115`
- Used to identify the button in click event handling

### 3. Button Initialization

**File**: `src/Lawn/Widget/GameSelector.cpp`

**Location**: Lines 193-204

```cpp
mPresentButton = MakeNewButton(
    GameSelector::GameSelector_Present,
    this,
    "",
    nullptr,
    Sexy::IMAGE_PRESENT,
    Sexy::IMAGE_PRESENT,
    Sexy::IMAGE_PRESENT
);
mPresentButton->Resize(260, 500, Sexy::IMAGE_PRESENT->mWidth, Sexy::IMAGE_PRESENT->mHeight);
mPresentButton->mClip = false;
mPresentButton->mMouseVisible = true;
```

**Description**:
- Creates the button using `MakeNewButton` helper function
- Parameters:
  - **ID**: `GameSelector::GameSelector_Present` (115)
  - **Listener**: `this` (GameSelector handles button events)
  - **Label**: `""` (empty string, no text label)
  - **Font**: `nullptr` (no font needed)
  - **Button Image**: `Sexy::IMAGE_PRESENT` (normal state)
  - **Over Image**: `Sexy::IMAGE_PRESENT` (hover state)
  - **Down Image**: `Sexy::IMAGE_PRESENT` (pressed state)
- **Position**: (260, 500) - bottom left area of the screen
- **Size**: Uses the image's natural width and height
- **Properties**:
  - `mClip = false`: Button can draw outside its bounds
  - `mMouseVisible = true`: Button responds to mouse events

### 4. Adding to Widget Manager

**File**: `src/Lawn/Widget/GameSelector.cpp`

**Location**: Line 1061

```cpp
void GameSelector::AddedToManager(WidgetManager* theWidgetManager)
{
    // ... other widgets added ...
    theWidgetManager->AddWidget(mPresentButton);
}
```

**Description**:
- Adds the button to the widget manager when GameSelector is displayed
- Makes the button visible and interactive

### 5. Removing from Widget Manager

**File**: `src/Lawn/Widget/GameSelector.cpp`

**Location**: Line 1086

```cpp
void GameSelector::RemovedFromManager(WidgetManager* theWidgetManager)
{
    // ... other widgets removed ...
    theWidgetManager->RemoveWidget(mPresentButton);
}
```

**Description**:
- Removes the button from the widget manager when GameSelector is closed
- Proper cleanup to prevent memory leaks

### 6. Mouse Visibility Control

**File**: `src/Lawn/Widget/GameSelector.cpp`

**Location**: Line 925

```cpp
mPresentButton->mMouseVisible = true;
```

**Description**:
- Sets the button to be mouse-visible when the selector is idle
- Part of the UI state management

### 7. Button Click Handler

**File**: `src/Lawn/Widget/GameSelector.cpp`

**Location**: Lines 1417-1420

```cpp
void GameSelector::ButtonDepress(int theId)
{
    // ... other button handling ...
    
    case GameSelector::GameSelector_Present:
        mApp->KillGameSelector();    // Close the main menu
        mApp->ShowMyWidget();         // Open the custom widget
        break;
}
```

**Description**:
- Handles the button click event
- **Actions**:
  1. `mApp->KillGameSelector()`: Closes the main menu (GameSelector)
  2. `mApp->ShowMyWidget()`: Opens the custom widget (MyWidget)
- This creates a transition from main menu to the custom interface

### 8. Memory Cleanup

**File**: `src/Lawn/Widget/GameSelector.cpp`

**Location**: Lines 418-419

```cpp
GameSelector::~GameSelector()
{
    // ... other cleanup ...
    if (mPresentButton)
        delete mPresentButton;
}
```

**Description**:
- Properly deletes the button in the destructor
- Prevents memory leaks

## Image Resource

The gift box button uses the `IMAGE_PRESENT` image resource. This is a standard game resource that displays a gift box icon.

## Related Files

| File | Purpose |
|------|---------|
| `GameSelector.h` | Button declaration and ID definition |
| `GameSelector.cpp` | Button initialization, event handling, and cleanup |
| `GameButton.h/cpp` | Base button class (not directly used, but related) |
| `NewLawnButton.h/cpp` | The actual button class used |

## Implementation Summary

To add a gift box button to the main menu:

1. **Declare** the button in the header file as `NewLawnButton*`
2. **Define** a unique button ID in the enum
3. **Initialize** the button in the constructor using `MakeNewButton`
4. **Add** the button to widget manager in `AddedToManager`
5. **Remove** the button from widget manager in `RemovedFromManager`
6. **Handle** click events in `ButtonDepress`
7. **Clean up** memory in the destructor

## Custom Widget Integration

The button opens a custom widget (`MyWidget`) which can be designed using SexyUI Editor. The workflow is:

1. Design the interface in SexyUI Editor
2. Export the generated code files
3. Implement `ShowMyWidget()` in `LawnApp` to create and display the widget
4. The button click triggers the transition from main menu to custom widget

## Notes

- The gift box button is positioned at (260, 500), which is in the lower-left area of the screen
- All three button states (normal, hover, pressed) use the same image (`IMAGE_PRESENT`)
- The button has no text label, relying solely on the image for visual representation
- The `mClip = false` setting allows the button to have visual effects that extend beyond its bounds
