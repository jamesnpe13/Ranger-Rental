import BookingStepper from "./components/BookingStepper";
import Button from "./components/Button";
import Chip from "./components/Chip";
import FooterBar from "./components/FooterBar";
import HeaderBar from "./components/HeaderBar";
import InputField from "./components/InputField";

function App() {
  return (
    <div className="frame">
      <HeaderBar />

      <div className="frame__container">
        <BookingStepper />
        <section>
          <InputField
            placeholder="Enter a keyword"
            buttonType="tertiary"
            buttonLabel="Search"
          />
          <br />
          <div className="chip-group">
            <Chip label="Blue" />
            <Chip label="FWD" />
            <Chip label="Hatchback" />
            <Chip label="Manual" />
            <Chip label="New" />
            <Chip label="Blue" />
            <Chip label="Hatchback" />
            <Chip label="New" />
            <Chip label="Auckland" />
            <Chip label="Available" />
          </div>
        </section>
        <hr />
        <section>
          <div className="section__container">
            <p>
              Lorem ipsum dolor sit amet consectetur, adipisicing elit. Maxime
              consequatur ad minus a cum, blanditiis deserunt nam veritatis
              earum provident atque, dolorum, amet sed. Ea nostrum laborum
              praesentium ratione quasi? Molestiae, pariatur nostrum? Atque,
              debitis numquam placeat fugit cum voluptatum, velit in
              necessitatibus maxime et eaque quam qui doloribus. Quos,
              reiciendis. Quasi error ex, enim aspernatur veniam consequuntur
              cumque unde! Reiciendis eaque voluptates, magni earum temporibus
              nostrum quasi accusantium odio a voluptatem incidunt quisquam
              assumenda soluta autem quod iste nesciunt unde suscipit
              exercitationem. Quidem ipsum dolorem, reiciendis enim sapiente
              nulla.
            </p>
            <div className="button-group">
              <Button type="primary">Primary Button</Button>
              {/* <Button type="secondary">Secondary Button</Button> */}
            </div>
          </div>
        </section>
        <hr />
        <section>
          <div className="section__container">
            <p>
              Lorem ipsum dolor sit amet consectetur, adipisicing elit. Maxime
              consequatur ad minus a cum, blanditiis deserunt nam veritatis
              earum provident atque, dolorum, amet sed. Ea nostrum laborum
              praesentium ratione quasi? Molestiae, pariatur nostrum? Atque,
              debitis numquam placeat fugit cum voluptatum, velit in
              necessitatibus maxime et eaque quam qui doloribus. Quos,
              reiciendis. Quasi error ex, enim aspernatur veniam consequuntur
              cumque unde! Reiciendis eaque voluptates, magni earum temporibus
              nostrum quasi accusantium odio a voluptatem incidunt quisquam
              assumenda soluta autem quod iste nesciunt unde suscipit
              exercitationem. Quidem ipsum dolorem, reiciendis enim sapiente
              nulla.
            </p>
            <div className="button-group">
              <Button type="primary">Primary</Button>
              <Button type="secondary">Secondary</Button>
              <Button type="tertiary">Tertiary</Button>
            </div>
            <div className="button-group">
              <Button type="destructive">Destructive</Button>
            </div>
            <div className="button-group">
              <Button type="text">Text button</Button>
            </div>
          </div>
        </section>
        <hr />
        <section>
          <div style={{ width: "80%" }}>
            <InputField placeholder="Filter vehicles" />
          </div>
        </section>

        <hr />

        <FooterBar />
      </div>
    </div>
  );
}

export default App;
