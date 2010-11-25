{% load custom_tags %}

#{{id}}.fraction.container.{{class}} title="{{type}}"

    .pnths.left {% conditional_display parenthesis %} 
        (

    .num
        {{num}}

    .den
        {{den}}

    .pnths.right {% conditional_display parenthesis %} 
        )
