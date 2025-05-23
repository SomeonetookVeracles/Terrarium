extends CharacterBody2D
@export var speed := 300.0

func _physics_process(delta):
	var input :=0
	if Input.is_action_pressed("ui_up"):
		input -= 1
	if Input.is_action_pressed("ui_down"):
		input += 1
		velocity = Vector2(0,input * speed)
		move_and_slide()
