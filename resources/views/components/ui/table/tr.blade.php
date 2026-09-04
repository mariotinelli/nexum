@props([
    'textAlign' => 'left',
])

<tr {{
    $attributes->class([
        'bg-white',
        'text-left'          => $textAlign === 'left',
        'w-full text-center' => $textAlign === 'center',
        'text-right'         => $textAlign === 'right',
    ])
}}>
    {{ $slot }}
</tr>
